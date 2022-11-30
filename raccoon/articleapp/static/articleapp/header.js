'use strict';
{
    $(() => {
        // ヘッダーのユーザーアイコン押下時にユーザーメニューを表示する
        const header_user_icon = $('header #header_user_icon');
        if (header_user_icon.length > 0) {
            const header_user_menu = $('header #header_user_menu');
            header_user_icon.click((e)=>{
                header_user_menu.toggle();
            });
        }
    });
}