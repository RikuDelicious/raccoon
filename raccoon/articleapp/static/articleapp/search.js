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

    // タグ検索用の処理 テキストを入力すると都度検索を行う(インクリメンタルサーチ)。
    $(() => {
        class Tag {
            constructor(id, name) {
                this.id = id;
                this.name = name;
            }
        }

        const CONTEXT = {
            tags_source: [], // array of Tag
            tags_filter: [], // array of Tag
            tags_filter_add: function (tagToAdd) {
                if (!this.tags_filter.some(tag => tag.id === tagToAdd.id)) {
                    this.tags_filter.push(tagToAdd);
                }
            },
            tags_filter_remove: function (tagToRemove) {
                this.tags_filter = this.tags_filter.filter(tag => tag.id !== tagToRemove.id);
            }
        }

        const SEARCH_URL = $('#tag_search_text').data("url");

        function updateTagsSourceView() {
            const tag_search_list = $('#tag_search_list');
            tag_search_list.empty();
            CONTEXT["tags_source"].forEach((tag) => {
                let li = $('<li>');
                let button = $('<button>', {
                    type: "button",
                    text: tag.name,
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
                if (CONTEXT["tags_filter"].some(tag_filter => tag_filter.id === tag.id)) {
                    li.hide();
                }

                tag_search_list.append(li);
            });
        }

        function updateTagsFilterView() {
            const tag_filter_list = $('#tag_filter_list');
            tag_filter_list.empty();
            CONTEXT["tags_filter"].forEach((tag) => {
                let li = $('<li>');
                let button = $('<button>', {
                    type: "button",
                    text: tag.name,
                });
                button.click((e) => {
                    CONTEXT.tags_filter_remove(tag);
                    updateTagsFilterView();
                    updateTagsSourceView();
                });
                li.append(button);
                tag_filter_list.append(li);
            });
        }

        function onSearchedTags(data) {
            // CONTEXT["tags_source"]を更新する
            let tagsFromData = data["tags"].map(tag => new Tag(tag["id"], tag["name"]));

            // 前回のタグ取得結果と同じならば、更新を行わない。
            if (tagsFromData.length === CONTEXT["tags_source"].length) {
                let isSameResult = true;

                for (let i = 0; i < tagsFromData.length; i++) {
                    if (tagsFromData[i].id !== CONTEXT["tags_source"][i].id) {
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

        $('#tag_search_text').on('input', (e) => {
            // 変換中は何もしない。ただし、以下のフラグで変換終了時も検索処理を行わなくなる。
            if (e.originalEvent.isComposing) {
                return;
            }

            requestNewSearch(e.target.value);
        });

        // 変換開始時に入力欄のテキストを保持しておく
        let text_before_compositionstart = '';
        $('#tag_search_text').on('compositionstart', (e) => {
            text_before_compositionstart = e.target.value;
        });

        // 変換終了時に別途検索処理を行う。
        $('#tag_search_text').on('compositionend', (e) => {
            // 変換完了時に変換開始時から変化が無ければ何もしない。
            if (text_before_compositionstart === e.target.value) {
                return;
            }

            requestNewSearch(e.target.value);
        });
    });
}