'use strict';
{
    $(() => {
        // 「フィルタ」ボタン押下時のアイコンアニメーションとアコーディオン開閉処理
        let inputs = $('#filter_period_input, #filter_tag_input, #filter_sort_input');
        let arrow_svg_anim = document.querySelector('#button_filter_accordion svg').animate(
            [
                { transform: 'rotate(0deg)' },
                { transform: 'rotate(180deg)' }
            ],
            {
                duration: 200,
                fill: 'forwards'
            }
        );
        arrow_svg_anim.addEventListener('finish', (e) => {
            arrow_svg_anim.reverse();
            arrow_svg_anim.pause();
        });
        arrow_svg_anim.pause();

        $('#button_filter_accordion').click((e) => {
            arrow_svg_anim.play()
            inputs.slideToggle();
        });
    });
}