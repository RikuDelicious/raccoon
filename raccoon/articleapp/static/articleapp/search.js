'use strict';
{
    $(() => {
        const FILTER_FORM = $('#filter_form');

        // 「フィルタ」ボタン押下時のアイコンアニメーションとアコーディオン開閉処理
        {
            let inputs = FILTER_FORM.find('#filter_period_input, #filter_tag_input, #filter_sort_input');
            let arrow_svg_anim = FILTER_FORM.find('#button_filter_accordion svg')[0].animate(
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
    
            FILTER_FORM.find('#button_filter_accordion').click((e) => {
                arrow_svg_anim.play()
                inputs.slideToggle();
            });
        }

        // フィルタ「投稿日」選択時に日付を算出して保持する
        // 「期間」選択時に入力欄のアクティブ・非アクティブを切り替える
        {
            const CONTEXT = {
                period_start_date: null, // null or Date
                period_end_date: null // null or Date
            };
    
            // フィルター表示部分の要素
            const period_filter_start = FILTER_FORM.find('#period_filter_start');
            const period_filter_end = FILTER_FORM.find('#period_filter_end');
    
            // 「期間」入力欄の要素
            const period_start_date = FILTER_FORM.find('#period_start_date');
            const period_start_date_label = FILTER_FORM.find('label[for=period_start_date]');
            const period_end_date = FILTER_FORM.find('#period_end_date');
            const period_end_date_label = FILTER_FORM.find('label[for=period_end_date]');
    
            // 送信前に隠しフィールドに値をセットする
            FILTER_FORM.submit((e) => {
                if (CONTEXT["period_start_date"] !== null) {
                    let start_date = CONTEXT["period_start_date"].getFullYear()
                        + '-' + (CONTEXT["period_start_date"].getMonth() + 1).toString().padStart(2, '0')
                        + '-' + CONTEXT["period_start_date"].getDate().toString().padStart(2, '0');
    
                    $(e.target).append($('<input>', {
                        type: 'hidden',
                        name: 'period_start_date',
                        value: start_date
                    }));
                }
    
                if (CONTEXT["period_end_date"] !== null) {
                    let end_date = CONTEXT["period_end_date"].getFullYear()
                        + '-' + (CONTEXT["period_end_date"].getMonth() + 1).toString().padStart(2, '0')
                        + '-' + CONTEXT["period_end_date"].getDate().toString().padStart(2, '0');
    
                    $(e.target).append($('<input>', {
                        type: 'hidden',
                        name: 'period_end_date',
                        value: end_date
                    }));
                }
            });
    
            function updateFilterHeader() {
                let start_date = '';
                if (CONTEXT["period_start_date"] !== null) {
                    start_date = CONTEXT["period_start_date"].getFullYear()
                        + '年' + (CONTEXT["period_start_date"].getMonth() + 1)
                        + '月' + CONTEXT["period_start_date"].getDate() + '日';
                }
    
                let end_date = '';
                if (CONTEXT["period_end_date"] !== null) {
                    end_date = CONTEXT["period_end_date"].getFullYear()
                        + '年' + (CONTEXT["period_end_date"].getMonth() + 1)
                        + '月' + CONTEXT["period_end_date"].getDate() + '日';
                }
    
                period_filter_start.text(start_date);
                period_filter_end.text(end_date);
            }
    
            function specify_period() {
                const start_date = Date.parse(period_start_date.val());
                const end_date = Date.parse(period_end_date.val());
    
                if (!Number.isNaN(start_date)) {
                    CONTEXT['period_start_date'] = new Date(start_date);
                }
                if (!Number.isNaN(end_date)) {
                    CONTEXT['period_end_date'] = new Date(end_date);
                }
            }

            FILTER_FORM.find('input[name=period]').change((e) => {
                const today = new Date();
                const value = FILTER_FORM.find('input[name=period]:checked').val();
    
                // value === 'period_unspecified'の場合は期間指定なしになる
                CONTEXT['period_start_date'] = null;
                CONTEXT['period_end_date'] = null;
    
                if (value === 'specify_period') {
                    period_start_date[0].toggleAttribute("disabled", false);
                    period_start_date_label.toggleClass('text-[#E6E6E6]', true);
                    period_end_date[0].toggleAttribute("disabled", false);
                    period_end_date_label.toggleClass('text-[#E6E6E6]', true);
    
                    specify_period();
                } else {
                    period_start_date[0].toggleAttribute("disabled", true);
                    period_start_date_label.toggleClass('text-[#E6E6E6]', false);
                    period_end_date[0].toggleAttribute("disabled", true);
                    period_end_date_label.toggleClass('text-[#E6E6E6]', false);
                }
    
                if (value === 'today') {
                    CONTEXT['period_start_date'] = today;
                    CONTEXT['period_end_date'] = today;
                } else if (value === 'thisweek') {
                    const monday = new Date(today.getTime());
                    let monday_offset = today.getDay() - 1;
                    if (monday_offset === -1) {
                        monday_offset = 6;
                    }
                    monday.setDate(today.getDate() - monday_offset);
                    CONTEXT['period_start_date'] = monday;
                    CONTEXT['period_end_date'] = today;
                } else if (value === 'thismonth') {
                    const month_first = new Date(today.getFullYear(), today.getMonth(), 1);
                    CONTEXT['period_start_date'] = month_first;
                    CONTEXT['period_end_date'] = today;
                } else if (value === 'thisyear') {
                    const year_first = new Date(today.getFullYear(), 0, 1);
                    CONTEXT['period_start_date'] = year_first;
                    CONTEXT['period_end_date'] = today;
                }
    
                updateFilterHeader();
            });
    
            FILTER_FORM.find('#period_start_date, #period_end_date').on('input', (e) => {
                CONTEXT['period_start_date'] = null;
                CONTEXT['period_end_date'] = null;
                specify_period();
                updateFilterHeader();
            });
    
    
            // ページ表示時にフィルタ「投稿日」入力欄でリクエストの条件を復元する
            {
                const queryString = window.location.search;
                const params = new URLSearchParams(queryString);
                const param_period = params.get('period');
                const period_values = ['specify_period', 'today', 'thisweek', 'thismonth', 'thisyear'];
                if (param_period !== null && period_values.includes(param_period) ) {
                    FILTER_FORM.find('input[name=period]').val([param_period]);
                    FILTER_FORM.find('input[name=period]').change();
                    if (param_period === 'specify_period') {
                        if (params.get('period_start_date') !== null) {
                            FILTER_FORM.find('#period_start_date').val(params.get('period_start_date'))
                            FILTER_FORM.find('#period_start_date').trigger('input');
                        }
    
                        if (params.get('period_end_date') !== null) {
                            FILTER_FORM.find('#period_end_date').val(params.get('period_end_date'))
                            FILTER_FORM.find('#period_end_date').trigger('input');
                        }
                    }
                }
            }
        }


        // タグ検索用の処理 テキストを入力すると都度検索を行う(インクリメンタルサーチ)。
        {
            class Tag {
                constructor(name) {
                    this.name = name;
                }
            }

            const CONTEXT = {
                tags_source: [], // array of Tag
                tags_filter: [], // array of Tag
                tags_filter_add: function (tagToAdd) {
                    if (!this.tags_filter.some(tag => tag.name === tagToAdd.name)) {
                        this.tags_filter.push(tagToAdd);
                    }
                },
                tags_filter_remove: function (tagToRemove) {
                    this.tags_filter = this.tags_filter.filter(tag => tag.name !== tagToRemove.name);
                }
            }

            const SEARCH_URL = FILTER_FORM.find('#tag_search_text').data("url");

            // 送信前に隠しフィールドでタグを送信する
            FILTER_FORM.submit((e) => {
                // バックエンドに以下の形式で配列のパラメータを送信する
                // ?tags=value1&tags=value2 => [value1, value2]
                CONTEXT["tags_filter"].forEach((tag) => {
                    const input = $('<input>', {
                        type: 'hidden',
                        name: 'tags',
                        value: tag.name
                    });
                    $(e.target).append(input);
                });
            });

            function updateTagsSourceView() {
                const tag_search_list = FILTER_FORM.find('#tag_search_list');
                tag_search_list.empty();
                CONTEXT["tags_source"].forEach((tag) => {
                    let li = $('<li>');
                    let button = $('<button>', {
                        type: "button",
                        text: '+ ' + tag.name,
                    });
                    button.click((e) => {
                        // フィルタ追加
                        CONTEXT.tags_filter_add(tag);
                        updateTagsFilterView();

                        // 検索結果一覧から非表示にする
                        li.hide();
                    });
                    li.append(button);

                    // 既にフィルタに追加済みのタグが検索結果に含まれている場合、
                    // そのタグは検索結果一覧には表示しない。
                    if (CONTEXT["tags_filter"].some(tag_filter => tag_filter.name === tag.name)) {
                        li.hide();
                    }

                    tag_search_list.append(li);
                });
            }

            function updateTagsFilterView() {
                const tag_filter_list = FILTER_FORM.find('#tag_filter_list');
                tag_filter_list.empty();
                CONTEXT["tags_filter"].forEach((tag) => {
                    let li = $('<li>', { 'class': 'tag_filter_item' });
                    let span = $('<span>', { text: tag.name });
                    let button = $('<button>', {
                        type: "button",
                    });
                    let x_mark = $('<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>');
                    button.click((e) => {
                        CONTEXT.tags_filter_remove(tag);
                        updateTagsFilterView();
                        updateTagsSourceView();
                    });
                    button.append(x_mark);
                    li.append(span, button);
                    tag_filter_list.append(li);
                });
            }

            function onSearchedTags(data) {
                // CONTEXT["tags_source"]を更新する
                let tagsFromData = data["tags"].map(tag => new Tag(tag["name"]));

                // 前回のタグ取得結果と同じならば、更新を行わない。
                if (tagsFromData.length === CONTEXT["tags_source"].length) {
                    let isSameResult = true;

                    for (let i = 0; i < tagsFromData.length; i++) {
                        if (tagsFromData[i].name !== CONTEXT["tags_source"][i].name) {
                            isSameResult = false;
                            break;
                        }
                    }

                    if (isSameResult) {
                        return;
                    }
                }

                // 更新
                CONTEXT["tags_source"] = tagsFromData;

                // CONTEXT["tags_source"]に基づいて検索結果一覧を表示
                updateTagsSourceView();
            }

            function search(keyword) {
                $.get(SEARCH_URL, { keyword: keyword }, onSearchedTags);
            }

            let isCoolTime = false;
            let nextRequest = null;
            function requestNewSearch(keyword) {
                if (isCoolTime) {
                    nextRequest = keyword;
                } else {
                    search(keyword);
                    nextRequest = null;
                    isCoolTime = true;
                    setTimeout(() => {
                        isCoolTime = false;
                        if (nextRequest !== null) {
                            search(nextRequest);
                        }
                    }, 1000);
                }
            }

            FILTER_FORM.find('#tag_search_text').on('input', (e) => {
                // 変換中は何もしない。ただし、以下のフラグで変換終了時も検索処理を行わなくなる。
                if (e.originalEvent.isComposing) {
                    return;
                }

                requestNewSearch(e.target.value);
            });

            // 変換開始時に入力欄のテキストを保持しておく
            let text_before_compositionstart = '';
            FILTER_FORM.find('#tag_search_text').on('compositionstart', (e) => {
                text_before_compositionstart = e.target.value;
            });

            // 変換終了時に別途検索処理を行う。
            FILTER_FORM.find('#tag_search_text').on('compositionend', (e) => {
                // 変換完了時に変換開始時から変化が無ければ何もしない。
                if (text_before_compositionstart === e.target.value) {
                    return;
                }

                requestNewSearch(e.target.value);
            });

            // ページ表示時にフィルタ「タグ」入力欄でリクエストの条件を復元する
            {
                const queryString = window.location.search;
                const params = new URLSearchParams(queryString);
                const param_tags = params.getAll('tags');
                param_tags.forEach((tag_name) => {
                    CONTEXT.tags_filter_add(new Tag(tag_name));
                    updateTagsFilterView();
                });
            }
        }
    });

    // 並び順選択時にヘッダー部分の表示を変更する
    $(() => {
        const sort_filter = $('#sort_filter');

        $('input[name=sort]').change((e) => {
            const value = $('input[name=sort]:checked').val();
            if (value === 'date_publish_desc') {
                sort_filter.text('新着順');
            } else if (value === 'date_publish_asc') {
                sort_filter.text('古い順');
            }
        });

        // ページ表示時にフィルタ「並び順」入力欄でリクエストの条件を復元する
        {
            const queryString = window.location.search;
            const params = new URLSearchParams(queryString);
            const param_sort = params.get('sort');
            const sort_values = ['date_publish_desc', 'date_publish_asc'];
            if (param_sort !== null && sort_values.includes(param_sort)) {
                $('input[name=sort]').val([param_sort]);
                $('input[name=sort]').change();
            } else {
                // デフォルト値は新着順にする
                $('input[name=sort]').val(['date_publish_desc']);
                $('input[name=sort]').change();
            }
        }
    });

    // 検索ボタンの送信イベント
    // 及び、キーワード入力フォームエンター時の送信イベントをここで実装する
    $(() => {
        $('#search_button').click((e) => {
            $('#filter_form').submit();
        });

        $('input[name=keyword]').keydown((e) => {
            if (e.which === 13) {
                $('#filter_form').submit();
            }
        });
    });
}