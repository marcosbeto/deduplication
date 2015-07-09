exports.build = function(array_json_str) {  
  return ['<!doctype html>',
  '<html lang="en"><meta charset="utf-8"></title>',
  '<script type="text/javascript" src="../api_connect.js" charset="utf-8"></script>',
  // '<link rel="stylesheet" href="/assets/style.css" />n',
  '<hw>{array_json}</h1>',
  '.']
  .join('')
  .replace(/{array_json}/g, array_json_str)
};