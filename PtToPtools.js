// ==UserScript==
// @name         PtToPtools
// @author       ngfchl
// @description  PT站点cookie等信息发送到Ptools
// @namespace    http://tampermonkey.net/

// @match        https://1ptba.com/userdetails.php?id=*
// @match        https://52pt.site/userdetails.php?id=*
// @match        https://audiences.me/userdetails.php?id=*
// @match        https://byr.pt/userdetails.php?id=*
// @match        https://ccfbits.org/userdetails.php?id=*
// @match        https://club.hares.top/userdetails.php?id=*
// @match        https://discfan.net/userdetails.php?id=*
// @match        https://et8.org/userdetails.php?id=*
// @match        https://filelist.io/userdetails.php?id=*
// @match        https://hdatmos.club/userdetails.php?id=*
// @match        https://hdchina.org/userdetails.php?id=*
// @match        https://hdcity.leniter.org/userdetails.php?id=*
// @match        https://hdhome.org/userdetails.php?id=*
// @match        https://hdmayi.com/userdetails.php?id=*
// @match        https://hdsky.me/userdetails.php?id=*
// @match        https://hdtime.org/userdetails.php?id=*
// @match        https://hudbt.hust.edu.cn/userdetails.php?id=*
// @match        https://iptorrents.com/t
// @match        https://kp.m-team.cc/userdetails.php?id=*
// @match        https://lemonhd.org/userdetails.php?id=*
// @match        https://nanyangpt.com/userdetails.php?id=*
// @match        https://npupt.com/userdetails.php?id=*
// @match        https://ourbits.club/userdetails.php?id=*
// @match        https://pt.btschool.club/userdetails.php?id=*
// @match        https://pt.eastgame.org/userdetails.php?id=*
// @match        https://pt.hdbd.us/userdetails.php?id=*
// @match        https://pt.keepfrds.com/userdetails.php?id=*
// @match        https://pterclub.com/userdetails.php?id=*
// @match        https://pthome.net/userdetails.php?id=*
// @match        https://springsunday.net/userdetails.php?id=*
// @match        https://totheglory.im/userdetails.php?id=*
// @match        https://u2.dmhy.org/userdetails.php?id=*
// @match        https://www.beitai.pt/userdetails.php?id=*
// @match        https://www.haidan.video/userdetails.php?id=*
// @match        https://www.hdarea.co/userdetails.php?id=*
// @match        https://www.hddolby.com/userdetails.php?id=*
// @match        https://www.htpt.cc/userdetails.php?id=*
// @match        https://www.nicept.net/userdetails.php?id=*
// @match        https://www.pthome.net/userdetails.php?id=*
// @match        https://www.pttime.org
// @match        https://www.tjupt.org/userdetails.php?id=*
// @match        https://www.torrentleech.org
// @match        https://www.carpet.net/userdetails.php?id=*
// @match        https://wintersakura.net/userdetails.php?id=*
// @match        https://hhanclub.top/userdetails.php?id=*
// @match        https://www.hdpt.xyz/userdetails.php?id=*
// @match        https://ptchina.org/userdetails.php?id=*
// @match        https://www.oshen.win/userdetails.php?id=*
// @match        https://www.hd.ai/userdetails.php?id=*
// @match        http://ihdbits.me/userdetails.php?id=*
// @match        https://zmpt.cc/userdetails.php?id=*
// @match        https://leaves.red/userdetails.php?id=*
// @match        https://piggo.me/userdetails.php?id=*
// @version      0.0.1
// @grant        GM_xmlhttpRequest
// @grant        none
// @license      GPL-3.0 License
// @require      https://cdn.bootcdn.net/ajax/libs/jquery/3.6.3/jquery.min.js
// ==/UserScript==

/*
日志：
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
    main();
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
    let href = document.location.search
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
    let res = await ajax_post(data)
    console.log(res)
    //await sendSiteToNastools(data);

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