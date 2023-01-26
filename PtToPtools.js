// ==UserScript==
// @name         PtToPtools
// @author       ngfchl
// @description  PT站点cookie等信息发送到Ptools
// @namespace    http://tampermonkey.net/

// @match        https://1ptba.com/*
// @match        https://52pt.site/*
// @match        https://audiences.me/*
// @match        https://byr.pt/*
// @match        https://ccfbits.org/*
// @match        https://club.hares.top/*
// @match        https://discfan.net/*
// @match        https://et8.org/*
// @match        https://filelist.io/*
// @match        https://hdatmos.club/*
// @match        https://hdchina.org/*
// @match        https://hdcity.leniter.org/*
// @match        https://hdhome.org/*
// @match        https://hdmayi.com/*
// @match        https://hdsky.me/*
// @match        https://hdtime.org/*
// @match        https://hudbt.hust.edu.cn/*
// @match        https://iptorrents.com/t
// @match        https://kp.m-team.cc/*
// @match        https://lemonhd.org/*
// @match        https://nanyangpt.com/*
// @match        https://npupt.com/*
// @match        https://ourbits.club/*
// @match        https://pt.btschool.club/*
// @match        https://pt.eastgame.org/*
// @match        https://pt.hdbd.us/*
// @match        https://pt.keepfrds.com/*
// @match        https://pterclub.com/*
// @match        https://pthome.net/*
// @match        https://springsunday.net/*
// @match        https://totheglory.im/*
// @match        https://u2.dmhy.org/*
// @match        https://www.beitai.pt/*
// @match        https://www.haidan.video/*
// @match        https://www.hdarea.co/*
// @match        https://www.hddolby.com/*
// @match        https://www.htpt.cc/*
// @match        https://www.nicept.net/*
// @match        https://www.pthome.net/*
// @match        https://www.pttime.org
// @match        https://www.tjupt.org/*
// @match        https://www.torrentleech.org
// @match        https://www.carpet.net/*
// @match        https://wintersakura.net/*
// @match        https://hhanclub.top/*
// @match        https://www.hdpt.xyz/*
// @match        https://ptchina.org/*
// @match        https://www.oshen.win/*
// @match        https://www.hd.ai/*
// @match        http://ihdbits.me/*
// @match        https://zmpt.cc/*
// @match        https://leaves.red/*
// @match        https://piggo.me/*
// @version      0.0.2
// @grant        GM_xmlhttpRequest
// @grant        none
// @license      GPL-3.0 License
// @require      https://cdn.bootcdn.net/ajax/libs/jquery/3.6.3/jquery.min.js
// ==/UserScript==

/*
日志：
    2023.01.26  更新逻辑，一小时内不会重复更新
    2023.01.25  完成第一版0.0.1
    2023.01.24  开始编写第一版脚本

*/
this.$ = this.jQuery = jQuery.noConflict(true);

// 设置ptools的访问地址，如http://192.168.1.2:8000
let ptools = "http://127.0.0.1:8000/";
// 获取安全密钥token，可以在ptools.toml中自定义，
// 格式 [token] token="ptools"
var token = "ptools";
var path = "tasks/monkey_to_ptools";


(function () {
    'use strict';
    main().then(res => {
        alert('PTools提醒您，你的Cookie已更新！')
    });
})();

async function getSite() {
    return $.ajax({
        url: ptools + path,
        type: "get",
        dataType: "json",
        data: {url: document.location.origin + '/', token: token}
    }).then(res => {
        // console.log(data);
        if (res.code !== 0) {
            console.error(res.msg)
            return
        }
        console.log('站点信息获取成功！', res.data)
        return res.data
    })
}

async function getData() {
    var site_info = await getSite()
    console.log(site_info)
    //获取cookie与useragent
    let user_agent = window.navigator.userAgent
    let cookie = document.cookie
    let re = /\d+/;
    let href = document.evaluate(site_info.uid_xpath, document).iterateNext()
    let user_id = re.exec(href)[0]
    return {
        user_id: user_id,
        site_id: site_info.site_id,
        cookie: cookie,
        token: token,
        user_agent: user_agent
    }
}

async function main() {
    var data = await getData();
    if (data == false) return;
    console.log(data)
    let res = await ajax_post(data).then(res => {
        alert('PTools提醒您：' + res.msg)
        console.log(res)
    })
}


async function ajax_post(data) {
    return $.ajax({
        type: "POST",
        url: ptools + path,
        dataType: "json",
        data: JSON.stringify(data),
    }).then(res => {
        console.log(res)
        return res
    });
}