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
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return {promise, resolve};
};

function sandbox({deferMicrophone=false, deferTurn=false}={}) {
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
  const fetch = async url => {
    if (url==="/api/config") return {ok:true,json:async()=>config};
    if (url==="/api/session") return {ok:true,json:async()=>({session_id:"session-"+(++sessionCount)})};
    if (url.startsWith("/api/turn")) {
      const turn=pending(); turns.push(turn);
      if (deferTurn) return turn.promise;
      return {ok:true,json:async()=>({
        transcript:{text:"hello",simulated:true},response:"Hello!",
        tool:null,audio_base64:null,
        metrics:{stt_ms:0,llm_ms:0,tools_ms:0,tts_ms:0,total_ms:0}
      })};
    }
    if (url.startsWith("/api/cancel")) return {ok:true};
    throw Error("Unexpected request: "+url);
  };
  const context = {
    document:{getElementById:element,createElement:()=>({append(){},textContent:""})},
    window:{MediaRecorder:Recorder,addEventListener:(name,fn)=>{listeners[name]=fn;}},
    navigator:{mediaDevices:{getUserMedia:()=>{
      micRequests.push(true);
      return deferMicrophone ? microphoneGate.promise : Promise.resolve(trackStream());
    }}},
    MediaRecorder:Recorder,fetch,Blob,FormData,AbortController,
    crypto:{randomUUID:()=>"req-"+turns.length},console
  };
  vm.runInNewContext(script, context, {filename:"voice-ui.js"});
  return {element, tracks, recorders, turns, listeners, micRequests, microphoneGate,
    trackStream, sessions:()=>sessionCount};
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