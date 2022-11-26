/**
 * 封装echarts，可以在vue中使用
 */

Vue.component('charts', {
    props: ['option', 'style'], data: function () {
        return {}
    }, mounted: function () {
        this.$nextTick(function () {
            var el = this.$el;
            var chart = echarts.init(el, 'dark');
            chart.setOption(this.option);
            this.chart = chart
        })
    }, watch: {
        obj: {
            option(newValue, oldValue) {
                // option发生变化时自动重新渲染
                this.chart.setOption(newValue)
            }, // immediate: true,
            deep: true,
        }

    }, template: '<div :style="style">{{option}}</div>'
})


