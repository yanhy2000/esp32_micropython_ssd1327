var http = require("http");
var url = require("url");
var font = require("./font");
var port = 3000 //设置服务端端口

http
  .createServer(function (request, response) {
    response.writeHead(200, { "Content-Type": "text/html;charset=utf-8" }); //设置response编码为utf-8
    var url_json = url.parse(request.url, true);
    var url_json_path = url_json.path;
    var url_path = "";
    var path = "";
    if (url_json_path != "/favicon.ico") {
      console.log(url_json_path);
      url_path = url_json_path.split("/");
      if (url_path != "") {
        path = url_path;
      }
    }
    //esp32模式
    if (path[1] == "esp32") {
      let type = path[2].split("?")[0];
      switch (type) { //预留多种请求
        case "font":
          {
            if (path[2].split("?").length == 2) {
              let msg = path[2].split("?")[1],
                str = msg.split("&")[0],
                size = msg.split("&")[1],
                str_num = JSON.parse(str).split("+"),
                font_code = [],
                t_code = ["0x"];
              for (let i = 0; i < str_num.length - 1; i++) {
                //循环总共多少个字
                t_code = font.font16[str_num[i]];
                console.log(t_code);
                font_code.push(t_code);
              }
              if (size == 16 || size == "") {
                for (let i = 0; i < font_code.length; i++) {
                  response.write("[" + font_code[i] + "]");
                  if (i < font_code.length - 1) {
                    response.write("+");
                  }
                }
              }
            }
          }
          break;
        default:
          break;
      }
    }
    response.end();
  })
  .listen(port);
console.log("--HTTP NodeJS Connect--\n已监听端口:", port);
