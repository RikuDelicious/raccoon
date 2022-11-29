def create_navigation_context_from_page(page):
    """
    ページネーションのリンクに表示するページ番号を決定して返す。

    Args:
        page (django.core.paginator.Page): 基準となるページ

    Returns:
        dict: 表示する番号一覧及び最初・最後の番号の表示有無
            {
                'numbers': list of page numbers to display.
                'display_first': True if display first page, False otherwise.
                'display_last': True if display last page, False otherwise.
            }
    """

    paginator = page.paginator
    numbers = []
    display_first = False
    display_last = False

    # 現在のページを中心として前後最大5ページ分を表示する
    # 上記の内、最初・最後のページを優先して表示する
    if paginator.num_pages >= 5:
        # 最初に、現在のページを真ん中にする
        left = page.number - 2
        right = page.number + 2
        # 左側か右側がページ範囲を逸脱する場合、その分を他方の側に加える
        if left < 1:
            right = right + (1 - left)
            left = 1
        elif right > paginator.num_pages:
            left = left - (right - paginator.num_pages)
            right = paginator.num_pages
        numbers = list(range(left, right + 1))
        # 左端が2以上の場合、左端の代わりに最初のページを表示する
        if left > 1:
            numbers.remove(left)
            display_first = True
        # 右端が最後のページの1個前以下の場合、代わりに最後のページを表示する
        if right < paginator.num_pages:
            numbers.remove(right)
            display_last = True
    else:
        numbers = list(range(1, paginator.num_pages + 1))

    return {
        "numbers": numbers,
        "display_first": display_first,
        "display_last": display_last,
    }
