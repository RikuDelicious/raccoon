'use strict';
{
    $(() => {
        const form = $('#post_form');

        /* markedでbodyフィールドのマークダウンのプレビューを表示する */
        const body_textarea = form.find('textarea[name=body]')
        const body_preview = $('#body_preview');
        marked.setOptions({
            breaks: true,
            highlight: function(code, lang) {
                const language = hljs.getLanguage(lang) ? lang: 'plaintext';
                return hljs.highlight(code, { language }).value;
            },
            langPrefix: 'hljs language-'
        });

        body_textarea.on('input', (e) => {
            body_preview.html(marked.parse($(e.target).val()));
        });

        /* 送信ボタンの送信イベントをここで実装する */
        form.find("#post_submit_button").click((e) => {
            form.submit();
        });
    });
}