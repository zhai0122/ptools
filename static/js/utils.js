function renderSize(value) {
    if (null == value || value == '') {
        return 0;
    }
    var unitArr = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    var index = 0;
    var srcsize = parseFloat(value);
    index = Math.floor(Math.log(srcsize) / Math.log(1024));
    var size = srcsize / Math.pow(1024, index);
    size = size.toFixed(3);//保留的小数位数
    return size + ' ' + unitArr[index];
}

function shuffle() {
    return Math.random() > 0.5 ? -1 : 1;
}

function numberFormat(value) {
    let param = {}
    let k = 10000
    let sizes = ['', 'W', 'E']
    let i
    if (value < k) {
        param.value = value
        param.unit = ''
    } else {
        i = Math.floor(Math.log(value) / Math.log(k));
        param.value = ((value / Math.pow(k, i))).toFixed(2);
        param.unit = sizes[i];
    }
    return `${param.value}${param.unit}`;
}
