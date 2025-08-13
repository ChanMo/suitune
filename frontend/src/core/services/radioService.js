export const radioService = {
  async next(channel = "music") {
    const resp = await fetch(`/api/next?channel=${channel}`);
    return resp.json();
  },
};
