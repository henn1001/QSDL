module.exports.readVersion = function (contents) {
  // matches __version__ = "2.0.1"
  // ignore groupt at start and end
  let match = contents.match(/(?:__version__ = \")(\d+\.\d+\.\d+)(?:\")/);

  // match[0] = '__version__ = "2.0.1"'
  // match[0] = '2.0.1',
  return match[1];
};

module.exports.writeVersion = function (contents, version) {
  let newContent = contents.replace(
    /__version__ = \"\d+\.\d+\.\d+\"/,
    `__version__ = "${version}"`
  );
  return newContent;
};
