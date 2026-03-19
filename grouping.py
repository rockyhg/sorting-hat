import random
from collections import defaultdict


def build_pair_counts(history: list[dict]) -> dict[tuple[str, str], int]:
    """履歴から各ペアが同じグループになった回数を集計する。"""
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for record in history:
        for group in record["groups"]:
            for i, a in enumerate(group):
                for b in group[i + 1 :]:
                    pair = tuple(sorted((a, b)))
                    counts[pair] += 1
    return counts


def _calc_score(groups: list[list[str]], pair_counts: dict[tuple[str, str], int]) -> int:
    """グループ割り当てのスコア（重複ペア回数の合計、低いほど良い）。"""
    score = 0
    for group in groups:
        for i, a in enumerate(group):
            for b in group[i + 1 :]:
                pair = tuple(sorted((a, b)))
                score += pair_counts.get(pair, 0)
    return score


def _distribute(members: list[str], num_groups: int) -> list[list[str]]:
    """メンバーをnum_groups個のグループにできるだけ均等に配分する。"""
    groups: list[list[str]] = [[] for _ in range(num_groups)]
    for i, m in enumerate(members):
        groups[i % num_groups].append(m)
    return groups


def assign_groups(
    members: list[str],
    history: list[dict],
    group_size: int | None = None,
    num_groups: int | None = None,
    attempts: int = 50,
) -> list[list[str]]:
    """
    メンバーをグループに分ける。

    group_size か num_groups のどちらか一方を指定する。
    履歴を考慮し、過去に同じグループになったペアをできるだけ避ける。
    """
    if group_size is None and num_groups is None:
        raise ValueError("group_size または num_groups のどちらかを指定してください")

    if len(members) == 0:
        return []

    if num_groups is None:
        num_groups = max(1, len(members) // group_size)

    num_groups = min(num_groups, len(members))

    pair_counts = build_pair_counts(history)

    best_groups = None
    best_score = float("inf")

    for _ in range(attempts):
        shuffled = members[:]
        random.shuffle(shuffled)
        groups = _distribute(shuffled, num_groups)

        # 局所探索: スワップで改善を試みる
        improved = True
        while improved:
            improved = False
            for gi in range(len(groups)):
                for gj in range(gi + 1, len(groups)):
                    for mi in range(len(groups[gi])):
                        for mj in range(len(groups[gj])):
                            # スワップ前のスコア
                            old_score = _calc_score(groups, pair_counts)
                            # スワップ
                            groups[gi][mi], groups[gj][mj] = groups[gj][mj], groups[gi][mi]
                            new_score = _calc_score(groups, pair_counts)
                            if new_score < old_score:
                                improved = True
                            else:
                                # 元に戻す
                                groups[gi][mi], groups[gj][mj] = groups[gj][mj], groups[gi][mi]

        score = _calc_score(groups, pair_counts)
        if score < best_score:
            best_score = score
            best_groups = [g[:] for g in groups]

        if best_score == 0:
            break

    return best_groups
