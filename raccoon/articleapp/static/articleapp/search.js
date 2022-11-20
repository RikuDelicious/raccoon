'use strict';
{
    // 「フィルタ」ボタン押下時のアイコンアニメーションとアコーディオン開閉処理
    $(() => {
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

    // 「期間」選択時の入力欄のアクティブ・非アクティブ切り替え
    $(() => {
        let period_start_date = $('#period_start_date')[0];
        let period_start_date_label = $('label[for=period_start_date]');
        let period_end_date = $('#period_end_date')[0];
        let period_end_date_label = $('label[for=period_end_date]');
        $('input[name=period]').change((e) => {
            let checked = $('input[name=period]:checked');
            if (checked.attr('id') === 'specify_period') {
                period_start_date.toggleAttribute("disabled", false);
                period_start_date_label.toggleClass('text-[#E6E6E6]', true);
                period_end_date.toggleAttribute("disabled", false);
                period_end_date_label.toggleClass('text-[#E6E6E6]', true);
            } else {
                period_start_date.toggleAttribute("disabled", true);
                period_start_date_label.toggleClass('text-[#E6E6E6]', false);
                period_end_date.toggleAttribute("disabled", true);
                period_end_date_label.toggleClass('text-[#E6E6E6]', false);
            }
        });
    });
}