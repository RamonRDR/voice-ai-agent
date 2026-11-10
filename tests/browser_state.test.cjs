"use strict";
const {test} = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");
const path = require("node:path");

const markup = fs.readFileSync(
  path.join(__dirname, "../src/voice_ai_agent/static/index.html"), "utf8"
);
const script = markup.split("<script>", 2)[1].split("</script>", 1)[0];
const settle = () => new Promise(resolve => setImmediate(resolve));
const pending = () => {
  let resolve, reject;
  const promise = new Promise((done, fail) => { resolve = done; reject = fail; });
  return {promise, resolve, reject};
};

function sandbox({deferMicrophone=false, deferFirstMicrophone=false, deferTurn=false, deferCancel=false}={}) {
  const nodes = new Map();
  const element = id => {
    if (!nodes.has(id)) {
      nodes.set(id, {
        id, disabled: false, value: id==="language" ? "en" : "",
        files: [], textContent: "", hidden: false, classList: {toggle(){}},
        querySelector(){return null;}, replaceChildren(){}, append(){},
      });
    }
    return nodes.get(id);
  };
  const tracks = [];
  const recorders = [];
  const turns = [];
  const listeners = {};
  const micRequests = [];
  const microphoneGate = pending();
  const cancellations = [];
  let sessionCount = 0;
  const config = {mode:"demo",stt:"demo",llm:"rules",tts:"browser",disclaimer:"Scripted demo"};
  class Recorder {
    static isTypeSupported() {return true;}
    constructor(stream, options) {
      this.stream=stream; this.mimeType=options?.mimeType || "audio/webm";
      this.state="inactive"; recorders.push(this);
    }
    start() {this.state="recording";}
    stop() {
      this.state="inactive";
      this.ondataavailable?.({data:new Blob(["some voice"],{type:"audio/webm"})});
      this.onstop?.();
    }
  }
  function trackStream() {
    const track = {stops:0, stop(){this.stops++;}};
    tracks.push(track);
    return {getTracks(){return [track];}};
  }
  const fetch = async (url, options={}) => {
    if (url==="/api/config") return {ok:true,json:async()=>config};
    if (url==="/api/session") return {ok:true,json:async()=>({session_id:"session-"+(++sessionCount)})};
    if (url.startsWith("/api/turn")) {
      const turn=pending(); turn.signal=options.signal; turns.push(turn);
      if (deferTurn) return turn.promise;
      return {ok:true,json:async()=>({
        transcript:{text:"hello",simulated:true},response:"Hello!",
        tool:null,audio_base64:null,
        metrics:{stt_ms:0,llm_ms:0,tools_ms:0,tts_ms:0,total_ms:0}
      })};
    }
    if (url.startsWith("/api/cancel")) {
      const cancel=pending(); cancel.url=url; cancellations.push(cancel);
      return deferCancel ? cancel.promise : {ok:true};
    }
    throw Error("Unexpected request: "+url);
  };
  const context = {
    document:{getElementById:element,createElement:()=>({append(){},textContent:""})},
    window:{MediaRecorder:Recorder,addEventListener:(name,fn)=>{listeners[name]=fn;}},
    navigator:{mediaDevices:{getUserMedia:()=>{
      micRequests.push(true);
      return deferMicrophone || (deferFirstMicrophone && micRequests.length===1)
        ? microphoneGate.promise : Promise.resolve(trackStream());
    }}},
    MediaRecorder:Recorder,fetch,Blob,FormData,AbortController,
    crypto:{randomUUID:()=>"req-"+turns.length},console
  };
  vm.runInNewContext(script, context, {filename:"voice-ui.js"});
  return {element, tracks, recorders, turns, cancellations, listeners, micRequests,
    microphoneGate, trackStream, sessions:()=>sessionCount};
}

test("recording blocks submissions and repeated microphone capture", async () => {
  const ui=sandbox({deferTurn:true});
  await settle();
  ui.element("typed").value="hello";
  const recording=ui.element("record").onclick();
  await recording;
  assert.equal(ui.recorders.length,1);
  assert.equal(ui.element("send").disabled,true);
  assert.equal(ui.element("send-file").disabled,true);
  assert.equal(ui.element("clear").disabled,true);
  ui.element("record").onclick();
  ui.element("send").onclick();
  ui.element("send-file").onclick();
  ui.element("clear").onclick();
  assert.equal(ui.recorders.length,1);
  assert.equal(ui.turns.length,0);
  assert.equal(ui.sessions(),1);
  ui.element("stop").onclick();
  assert.equal(ui.turns.length,1);
  assert.equal(ui.tracks[0].stops,1);
  assert.equal(ui.element("record").disabled,true);
  ui.element("record").onclick();
  ui.element("send").onclick();
  assert.equal(ui.recorders.length,1);
  assert.equal(ui.turns.length,1);
  ui.turns[0].resolve({ok:true,json:async()=>({
    transcript:{text:"hello",simulated:true},response:"Hello!",
    tool:null,audio_base64:null,
    metrics:{stt_ms:0,llm_ms:0,tools_ms:0,tts_ms:0,total_ms:0}
  })});
  await settle();
  assert.equal(ui.element("record").disabled,false);
  assert.equal(ui.element("send").disabled,false);
  await ui.element("record").onclick();
  assert.equal(ui.recorders.length,2);
  ui.listeners.pagehide();
  assert.equal(ui.tracks[1].stops,1);
});

test("microphone acquisition remains locked and pagehide releases a late stream", async () => {
  const ui=sandbox({deferMicrophone:true});
  await settle();
  const recording=ui.element("record").onclick();
  assert.equal(ui.element("send").disabled,true);
  assert.equal(ui.element("record").disabled,true);
  ui.element("record").onclick();
  ui.element("send").onclick();
  ui.element("clear").onclick();
  assert.equal(ui.micRequests.length,1);
  assert.equal(ui.sessions(),1);
  ui.listeners.pagehide();
  const captured=ui.trackStream();
  ui.microphoneGate.resolve(captured);
  await recording;
  assert.equal(ui.recorders.length,0);
  assert.equal(ui.tracks[0].stops,1);
  assert.equal(ui.element("record").disabled,true);
});

test("a stopped recording submits only one turn and releases its audio track", async () => {
  const ui=sandbox();
  await settle();
  await ui.element("record").onclick();
  assert.equal(ui.element("stop").disabled,false);
  assert.equal(ui.tracks[0].stops,0);
  ui.element("stop").onclick();
  ui.element("stop").onclick();
  await settle();
  assert.equal(ui.tracks[0].stops,1);
  assert.equal(ui.turns.length,1);
  assert.equal(ui.element("stop").disabled,true);
  assert.equal(ui.element("send").disabled,false);
});

function successfulTurn() {
  return {ok:true,json:async()=>({
    transcript:{text:"hello",simulated:true},response:"Hello!",
    tool:null,audio_base64:null,
    metrics:{stt_ms:0,llm_ms:0,tools_ms:0,tts_ms:0,total_ms:0}
  })};
}

test("late cancellation only aborts its own request and cannot replace a newer status", async () => {
  const ui=sandbox({deferTurn:true,deferCancel:true});
  await settle();
  ui.element("typed").value="first";
  ui.element("send").onclick();
  assert.equal(ui.turns.length,1);
  const first=ui.turns[0];
  const cancel=ui.element("cancel").onclick();
  assert.equal(ui.cancellations.length,1);
  assert.equal(ui.element("cancel").disabled,true);
  assert.match(ui.cancellations[0].url,/\/api\/cancel\/req-0\?/);

  first.resolve(successfulTurn());
  await settle();
  assert.equal(ui.element("send").disabled,false);
  ui.element("typed").value="second";
  ui.element("send").onclick();
  assert.equal(ui.turns.length,2);
  const second=ui.turns[1];
  assert.equal(second.signal.aborted,false);
  const processingStatus=ui.element("status").textContent;
  assert.match(processingStatus,/Processing text/);

  ui.cancellations[0].resolve({ok:true});
  await cancel;
  assert.equal(first.signal.aborted,true);
  assert.equal(second.signal.aborted,false);
  assert.equal(ui.element("status").textContent,processingStatus);
  assert.equal(ui.element("cancel").disabled,false);

  second.resolve(successfulTurn());
  await settle();
  assert.equal(ui.element("send").disabled,false);
});

test("BFCache pageshow reinitializes a closed page after microphone cleanup", async () => {
  const ui=sandbox();
  await settle();
  await ui.element("record").onclick();
  assert.equal(ui.element("stop").disabled,false);
  ui.listeners.pagehide({persisted:true});
  assert.equal(ui.tracks[0].stops,1);
  assert.equal(ui.element("send").disabled,true);
  assert.equal(ui.element("record").disabled,true);
  ui.listeners.pageshow({persisted:true});
  await settle();
  assert.equal(ui.sessions(),2);
  assert.equal(ui.element("record").disabled,false);
  assert.equal(ui.element("send").disabled,false);
  assert.equal(ui.element("language").disabled,false);
  assert.equal(ui.element("clear").disabled,false);
  assert.equal(ui.element("stop").disabled,true);
  assert.equal(ui.element("cancel").disabled,true);
  await ui.element("record").onclick();
  assert.equal(ui.recorders.length,2);
  ui.listeners.pagehide({persisted:true});
  assert.equal(ui.tracks[1].stops,1);
});

test("BFCache restores controls without accepting stale HTTP turn callbacks", async () => {
  const ui=sandbox({deferTurn:true});
  await settle();
  ui.element("typed").value="old request";
  ui.element("send").onclick();
  const old=ui.turns[0];
  ui.listeners.pagehide({persisted:true});
  assert.equal(old.signal.aborted,true);
  ui.listeners.pageshow({persisted:true});
  await settle();
  assert.equal(ui.sessions(),2);
  const status=ui.element("status").textContent;
  assert.equal(status,"New private in-memory session created.");
  old.resolve(successfulTurn());
  await settle();
  assert.equal(ui.element("status").textContent,status);
  assert.equal(ui.element("record").disabled,false);
  assert.equal(ui.element("send").disabled,false);
  assert.equal(ui.element("conversation").textContent,"");
  ui.element("typed").value="new request";
  ui.element("send").onclick();
  assert.equal(ui.turns.length,2);
  assert.equal(ui.turns[1].signal.aborted,false);
  ui.turns[1].resolve(successfulTurn());
  await settle();
  assert.equal(ui.element("send").disabled,false);
});

test("a permission granted after BFCache navigation cannot start an old recorder", async () => {
  const ui=sandbox({deferMicrophone:true});
  await settle();
  const old=ui.element("record").onclick();
  ui.listeners.pagehide({persisted:true});
  ui.listeners.pageshow({persisted:true});
  await settle();
  assert.equal(ui.element("record").disabled,false);
  const stale=ui.trackStream();
  ui.microphoneGate.resolve(stale);
  await old;
  assert.equal(ui.recorders.length,0);
  assert.equal(stale.getTracks()[0].stops,1);
  assert.equal(ui.element("record").disabled,false);
});


test("stale microphone permission rejection cannot clear a newer recording", async () => {
  const ui=sandbox({deferFirstMicrophone:true,deferTurn:true});
  await settle();

  const oldPermission=ui.element("record").onclick();
  assert.equal(ui.recorders.length,0);
  assert.equal(ui.element("record").disabled,true);
  ui.listeners.pagehide({persisted:true});
  ui.listeners.pageshow({persisted:true});
  await settle();

  // Start a new, independent recording while the old permission prompt is pending.
  await ui.element("record").onclick();
  assert.equal(ui.micRequests.length,2);
  assert.equal(ui.recorders.length,1);
  const current=ui.recorders[0];
  assert.equal(current.state,"recording");
  assert.equal(ui.element("stop").disabled,false);
  assert.equal(ui.tracks[0].stops,0);
  const status=ui.element("status").textContent;

  // The previous page's permission denial must not touch the current recorder/UI.
  ui.microphoneGate.reject(new Error("Previous page microphone permission denied"));
  await oldPermission;
  assert.equal(ui.element("status").textContent,status);
  assert.equal(current.state,"recording");
  assert.equal(ui.element("record").disabled,true);
  assert.equal(ui.element("stop").disabled,false);
  assert.equal(ui.tracks[0].stops,0);

  ui.element("stop").onclick();
  assert.equal(current.state,"inactive");
  assert.equal(ui.tracks[0].stops,1);
  assert.equal(ui.turns.length,1);
  ui.turns[0].resolve(successfulTurn());
  await settle();
  assert.equal(ui.element("record").disabled,false);
  assert.equal(ui.element("stop").disabled,true);
});
