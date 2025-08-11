# ui/stats_top5_cli.py
# Print-once Top-5 dashboard (dataset-centric).

from features.trie_stats import compute_stats, pretty_print

def show_stats_menu(trie):
    stats = compute_stats(trie, top_k=5)
    pretty_print(stats)