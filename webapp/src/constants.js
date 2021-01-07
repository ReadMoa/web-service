// The base path for ReadMoa APIs.
export function getApiServerPath() {
  if (process.env.NODE_ENV === "production") {
    return "/api/";
  }
  // If the environment is 'development' or 'testing'.
  return "http://127.0.0.1:8080/api/";
}
