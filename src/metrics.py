from answer_quality_metrics import calculate_Kendalls_Tau, calculate_recall, calculate_supporting_association, get_gpt_key_point_offsets, prompt_claim_comparison, update_offsets
from common import print_str_list
from thoughts_from_articles import get_gpt, run_answer_key_point_extraction
from utils import null_or_empty


def compare_with_gold_answer(question, gold_answer, other_answer):
    key_points = run_answer_key_point_extraction(question, other_answer)
    print(key_points)

    top_level_kps = [x["top_level_key_point"] for x in gold_answer]
    gpt_coverage_0 = get_gpt(
        prompt_claim_comparison,
        ["output"],
        question=question,
        key_points_0=top_level_kps,
        key_points_1=key_points,
        print_func=print_str_list,
    )
    coverage_0 = gpt_coverage_0.run({})
    top_level_recall = calculate_recall(coverage_0, len(top_level_kps))

    supporting_kps = [x.get("supporting_key_points", []) for x in gold_answer]
    supporting_kps = [item for sublist in supporting_kps for item in sublist]
    gpt_coverage_1 = get_gpt(
        prompt_claim_comparison,
        ["output"],
        question=question,
        key_points_0=supporting_kps,
        key_points_1=key_points,
        print_func=print_str_list,
    )
    coverage_1 = gpt_coverage_1.run({})
    supporting_recall = calculate_recall(coverage_1, len(supporting_kps))

    gpt_top_level_offsets = get_gpt_key_point_offsets(
        other_answer, top_level_kps, print_str_list
    )
    top_level_offsets = gpt_top_level_offsets.run({})
    update_offsets(top_level_offsets, top_level_kps, coverage_0, other_answer)
    relevance = calculate_Kendalls_Tau(top_level_offsets)

    if null_or_empty(supporting_kps):
        supporting_offsets = None
        semantic_coherence = None
    else:
        gpt_supporting_offsets = get_gpt_key_point_offsets(
            other_answer, supporting_kps, print_str_list
        )
        supporting_offsets = gpt_supporting_offsets.run({})
        update_offsets(supporting_offsets, supporting_kps, coverage_1, other_answer)
        semantic_coherence = calculate_supporting_association(
            gold_answer, top_level_offsets, supporting_offsets
        )
    return {
        "top_level_recall": top_level_recall,
        "supporting_recall": supporting_recall,
        "relevance": relevance,
        "semantic_coherence": semantic_coherence,
        "answer": other_answer,
        "gold_answer": gold_answer,
        "top_level_offsets": top_level_offsets,
        "supporting_offsets": supporting_offsets,
        "top_level_coverage": coverage_0,
        "supporting_coverage": coverage_1,
    }
