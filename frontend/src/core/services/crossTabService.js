export const crossTabService = {
  channel: new BroadcastChannel("suitune-player"),
  send(msg) {
    this.channel.postMessage(msg);
  },
};
