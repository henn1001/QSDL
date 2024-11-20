module.exports.readVersion = function (contents) {
  // matches version = "2.0.1"
  // ignore groupt at start and end
  let match = contents.match(/(?:version = \")(\d+\.\d+\.\d+)(?:\")/);
  // match[0] = 'version = "2.0.1"'
  // match[0] = '2.0.1',
  return match[1];
};
module.exports.writeVersion = function (contents, version) {
  let newContent = contents.replace(/version = \"\d+\.\d+\.\d+\"/, `version = "${version}"`);
  return newContent;
};
