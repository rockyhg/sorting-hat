"""grouping モジュールのテスト。

組分けロジック（ペア集計・スコア計算・均等配分・グループ割り当て）を検証する。
"""

import pytest

from grouping import assign_groups, build_pair_counts, _calc_score, _distribute


class TestBuildPairCounts:
    """build_pair_counts: 履歴からペア同席回数を集計する関数のテスト。"""

    def test_empty_history(self):
        """履歴が空の場合、空の辞書を返す。"""
        assert build_pair_counts([]) == {}

    def test_single_record(self):
        """1件の履歴から全ペアがカウント1で集計される。"""
        history = [{"groups": [["A", "B", "C"]]}]
        counts = build_pair_counts(history)
        assert counts[("A", "B")] == 1
        assert counts[("A", "C")] == 1
        assert counts[("B", "C")] == 1

    def test_multiple_records(self):
        """複数の履歴で同じペアが繰り返された場合、回数が累積される。"""
        history = [
            {"groups": [["A", "B"], ["C", "D"]]},
            {"groups": [["A", "B"], ["C", "D"]]},
        ]
        counts = build_pair_counts(history)
        assert counts[("A", "B")] == 2
        assert counts[("C", "D")] == 2
        assert counts.get(("A", "C"), 0) == 0

    def test_pair_order_is_sorted(self):
        """ペアのキーはアルファベット順にソートされる。"""
        history = [{"groups": [["B", "A"]]}]
        counts = build_pair_counts(history)
        assert ("A", "B") in counts
        assert ("B", "A") not in counts


class TestCalcScore:
    """_calc_score: グループ割り当てのスコア（重複ペア回数の合計）を計算する関数のテスト。"""

    def test_no_overlap(self):
        """過去のペアと重複がない場合、スコアは0になる。"""
        groups = [["A", "B"], ["C", "D"]]
        pair_counts = {("A", "C"): 1, ("B", "D"): 1}
        assert _calc_score(groups, pair_counts) == 0

    def test_with_overlap(self):
        """過去のペアと重複がある場合、その回数の合計がスコアになる。"""
        groups = [["A", "B"], ["C", "D"]]
        pair_counts = {("A", "B"): 3, ("C", "D"): 2}
        assert _calc_score(groups, pair_counts) == 5


class TestDistribute:
    """_distribute: メンバーを指定数のグループに均等配分する関数のテスト。"""

    def test_even_distribution(self):
        """メンバー数がグループ数で割り切れる場合、各グループのサイズが等しい。"""
        groups = _distribute(["A", "B", "C", "D"], 2)
        assert len(groups) == 2
        assert all(len(g) == 2 for g in groups)

    def test_uneven_distribution(self):
        """メンバー数がグループ数で割り切れない場合、サイズの差は最大1になる。"""
        groups = _distribute(["A", "B", "C", "D", "E"], 2)
        sizes = sorted(len(g) for g in groups)
        assert sizes == [2, 3]

    def test_single_group(self):
        """グループ数が1の場合、全メンバーが1つのグループに入る。"""
        groups = _distribute(["A", "B", "C"], 1)
        assert len(groups) == 1
        assert len(groups[0]) == 3

    def test_all_members_present(self):
        """配分後、全メンバーが漏れなく含まれている。"""
        members = ["A", "B", "C", "D", "E"]
        groups = _distribute(members, 3)
        flat = sorted(m for g in groups for m in g)
        assert flat == sorted(members)


class TestAssignGroups:
    """assign_groups: 履歴を考慮したグループ割り当てのテスト。"""

    def test_with_group_size(self):
        """group_size 指定で正しいグループ数に分割される。"""
        members = ["A", "B", "C", "D"]
        result = assign_groups(members, history=[], group_size=2)
        flat = sorted(m for g in result for m in g)
        assert flat == sorted(members)
        assert len(result) == 2

    def test_with_num_groups(self):
        """num_groups 指定で正しいグループ数に分割される。"""
        members = ["A", "B", "C", "D", "E", "F"]
        result = assign_groups(members, history=[], num_groups=3)
        assert len(result) == 3

    def test_empty_members(self):
        """メンバーが空の場合、空リストを返す。"""
        assert assign_groups([], history=[], group_size=2) == []

    def test_requires_group_size_or_num_groups(self):
        """group_size も num_groups も未指定の場合、ValueError を送出する。"""
        with pytest.raises(ValueError):
            assign_groups(["A", "B"], history=[])

    def test_avoids_past_pairs(self):
        """過去に繰り返し同席したペアを別グループに分ける。"""
        members = ["A", "B", "C", "D"]
        history = [
            {"groups": [["A", "B"], ["C", "D"]]},
            {"groups": [["A", "B"], ["C", "D"]]},
            {"groups": [["A", "B"], ["C", "D"]]},
        ]
        result = assign_groups(members, history, num_groups=2, attempts=100)
        for group in result:
            assert not ({"A", "B"} <= set(group))

    def test_num_groups_capped_by_member_count(self):
        """num_groups がメンバー数を超える場合、メンバー数に制限される。"""
        members = ["A", "B"]
        result = assign_groups(members, history=[], num_groups=5)
        assert len(result) == 2

    def test_all_members_assigned(self):
        """全メンバーがいずれかのグループに割り当てられている。"""
        members = ["A", "B", "C", "D", "E"]
        result = assign_groups(members, history=[], group_size=2)
        flat = sorted(m for g in result for m in g)
        assert flat == sorted(members)
