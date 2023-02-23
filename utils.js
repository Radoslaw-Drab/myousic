const { exec } = require("child_process");
const readline = require("readline").createInterface({
  input: process.stdin,
  output: process.stdout,
});
function lineBreaker(before = false, after = false) {
  if (before) console.log("\n");
  console.log("+" + "-".repeat(process.stdout.columns - 1 || 100));
  if (after) console.log("\n");
}
function errorPrompt(text) {
  lineBreaker();
  console.log(`|\n|  ${text}\n|`);
  lineBreaker();
  readline.close();
}
function question(text) {
  return new Promise((resolve) => {
    readline.question(text, resolve);
  });
}
async function getCommands(...commands) {
  const promises = commands.map((command) => {
    return new Promise((resolve, reject) => {
      exec(command, (error, stdout) => {
        if (error) reject(error);
        return resolve(stdout.replaceAll("\n", ""));
      });
    });
  });
  const cmds = Promise.allSettled(promises);
  (await cmds).forEach((cmd, i) => (cmd.cmd = commands[i]));
  return cmds;
}

function copyrights() {
  lineBreaker();
  console.log("|  Provided by iTunes");
}
module.exports = {
  lineBreaker,
  errorPrompt,
  question,
  getCommands,
  copyrights,
  readline,
};
