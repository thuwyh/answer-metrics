# answer-metrics

Main function: `src.metrics.compare_with_gold_answer`

How to use: see `src/example.py`
You will get result like below

```
{
  "top_level_recall": 0.7,
  "supporting_recall": 0.45,
  "relevance": -0.6666666666666666,
  "semantic_coherence": 0.4,
  "answer": "In the 2024 Oklahoma elections, Donald Trump won the state with 66.17% of the vote, maintaining Oklahoma's Republican dominance [[1](https://www.pryorinfopub.com/news/oklahoma-election-recap-high-turnout-big-wins-and-key-decisions/article_c5b190ba-9c41-11ef-b49c-d3bc938bab21.html)]. Despite a record number of registered voters, Oklahoma experienced the lowest voter turnout in the nation, with only 53% of eligible voters participating, marking a decline from previous presidential elections [[2](https://oklahomavoice.com/2024/11/06/oklahoma-voter-turnout-lowest-in-the-nation-drops-from-previous-presidential-elections/)],[[3](https://www.oklahoman.com/story/news/politics/2024/11/06/election-results-oklahoma-voter-turnout-in-fell-in-2024/76089629007/)].\n\n- **Voter Registration and Turnout**: Oklahoma had a record 2.4 million registered voters, but turnout was only 64% among registered voters, a decrease from 69% in 2020 [[2](https://oklahomavoice.com/2024/11/06/oklahoma-voter-turnout-lowest-in-the-nation-drops-from-previous-presidential-elections/)],[[3](https://www.oklahoman.com/story/news/politics/2024/11/06/election-results-oklahoma-voter-turnout-in-fell-in-2024/76089629007/)].\n- **State Elections**: Republicans retained their supermajority in the state Senate, winning several key races [[4](https://www.oklahoman.com/story/news/politics/elections/2024/11/05/oklahoma-senate-election-2024-results/75988381007/)].\n- **Ballot Measures**: Oklahoma voters passed State Question 834 overwhelmingly, while State Question 833 failed [[1](https://www.pryorinfopub.com/news/oklahoma-election-recap-high-turnout-big-wins-and-key-decisions/article_c5b190ba-9c41-11ef-b49c-d3bc938bab21.html)].\n\nThe election highlighted Oklahoma's consistent support for Republican candidates and revealed a trend of low voter engagement despite high registration numbers and early voting participation.\n\n",
  "gold_answer": [
    {
      "top_level_key_point": "All incumbent Republican U.S. House Representatives from Oklahoma were re-elected.",
      "supporting_key_points": [
        "Representatives Kevin Hern, Josh Brecheen, Tom Cole, and Stephanie Bice all won their respective districts.",
        "These victories reflect continued Republican dominance in Oklahoma's congressional delegation."
      ]
    },
    {
      "top_level_key_point": "Donald Trump won the presidential election in Oklahoma, securing all seven electoral votes.",
      "supporting_key_points": [
        "Trump's victory was declared by multiple sources including the Associated Press.",
        "He has historically won Oklahoma in previous elections, maintaining a strong Republican presence."
      ]
    },
    {
      "top_level_key_point": "Brian Bingman won the election for Oklahoma Corporation Commissioner.",
      "supporting_key_points": [
        "Bingman's victory fills one of the three seats on the Commission, with no incumbent in the race.",
        "The Oklahoma Corporation Commission plays a crucial role in regulating utilities and energy."
      ]
    },
    {
      "top_level_key_point": "Oklahoma voters decided on two state questions with differing outcomes.",
      "supporting_key_points": [
        "State Question 833, which would have allowed cities to create public infrastructure districts, was rejected.",
        "State Question 834, which amended the state constitution to specify that only American citizens can vote, was approved."
      ]
    },
    {
      "top_level_key_point": "Voter turnout in Oklahoma showed mixed results with an overall decrease in participation despite higher registration.",
      "supporting_key_points": [
        "While more Oklahomans registered and more votes were cast for president than in previous years, the percentage of voter participation actually decreased.",
        "Oklahoma County and rural counties experienced significant variations in voter turnout."
      ]
    }
  ],
  "top_level_offsets": {
    "output": [
      {
        "key_point_index": 2,
        "original_text_chunk": "In the 2024 Oklahoma elections, Donald Trump won the state with 66.17% of the vote, maintaining Oklahoma's Republican dominance",
        "from": 0,
        "to": 128,
        "kp": "Donald Trump won the presidential election in Oklahoma, securing all seven electoral votes."
      },
      {
        "key_point_index": 4,
        "original_text_chunk": "Oklahoma voters passed State Question 834 overwhelmingly, while State Question 833 failed",
        "from": 1473,
        "to": 1562,
        "kp": "Oklahoma voters decided on two state questions with differing outcomes."
      },
      {
        "key_point_index": 5,
        "original_text_chunk": "Despite a record number of registered voters, Oklahoma experienced the lowest voter turnout in the nation, with only 53% of eligible voters participating, marking a decline from previous presidential elections",
        "from": 290,
        "to": 498,
        "kp": "Voter turnout in Oklahoma showed mixed results with an overall decrease in participation despite higher registration."
      }
    ]
  },
  "supporting_offsets": {
    "output": [
      {
        "key_point_index": 1,
        "original_text_chunk": "State Elections: Republicans retained their supermajority in the state Senate, winning several key races",
        "from": "",
        "to": ""
      },
      {
        "key_point_index": 2,
        "original_text_chunk": "State Elections: Republicans retained their supermajority in the state Senate, winning several key races",
        "from": 1215,
        "to": 1321,
        "kp": "These victories reflect continued Republican dominance in Oklahoma's congressional delegation."
      },
      {
        "key_point_index": 3,
        "original_text_chunk": "In the 2024 Oklahoma elections, Donald Trump won the state with 66.17% of the vote",
        "from": 0,
        "to": 82,
        "kp": "Trump's victory was declared by multiple sources including the Associated Press."
      },
      {
        "key_point_index": 4,
        "original_text_chunk": "In the 2024 Oklahoma elections, Donald Trump won the state with 66.17% of the vote",
        "from": "",
        "to": ""
      },
      {
        "key_point_index": 7,
        "original_text_chunk": "Ballot Measures: Oklahoma voters passed State Question 834 overwhelmingly, while State Question 833 failed",
        "from": 1454,
        "to": 1562,
        "kp": "State Question 833, which would have allowed cities to create public infrastructure districts, was rejected."
      },
      {
        "key_point_index": 8,
        "original_text_chunk": "Ballot Measures: Oklahoma voters passed State Question 834 overwhelmingly, while State Question 833 failed",
        "from": 1454,
        "to": 1562,
        "kp": "State Question 834, which amended the state constitution to specify that only American citizens can vote, was approved."
      },
      {
        "key_point_index": 9,
        "original_text_chunk": "Despite a record number of registered voters, Oklahoma experienced the lowest voter turnout in the nation, with only 53% of eligible voters participating, marking a decline from previous presidential elections",
        "from": 290,
        "to": 498,
        "kp": "While more Oklahomans registered and more votes were cast for president than in previous years, the percentage of voter participation actually decreased."
      },
      {
        "key_point_index": 10,
        "original_text_chunk": "Despite a record number of registered voters, Oklahoma experienced the lowest voter turnout in the nation, with only 53% of eligible voters participating, marking a decline from previous presidential elections",
        "from": "",
        "to": ""
      }
    ]
  },
  "top_level_coverage": {
    "output": [
      {
        "claim_id_in_set_A": 1,
        "coverage_percentage_by_set_B": 0.5
      },
      {
        "claim_id_in_set_A": 2,
        "coverage_percentage_by_set_B": 1
      },
      {
        "claim_id_in_set_A": 3,
        "coverage_percentage_by_set_B": 0
      },
      {
        "claim_id_in_set_A": 4,
        "coverage_percentage_by_set_B": 1
      },
      {
        "claim_id_in_set_A": 5,
        "coverage_percentage_by_set_B": 1
      }
    ]
  },
  "supporting_coverage": {
    "output": [
      {
        "claim_id_in_set_A": 1,
        "coverage_percentage_by_set_B": 0
      },
      {
        "claim_id_in_set_A": 2,
        "coverage_percentage_by_set_B": 1
      },
      {
        "claim_id_in_set_A": 3,
        "coverage_percentage_by_set_B": 1
      },
      {
        "claim_id_in_set_A": 4,
        "coverage_percentage_by_set_B": 0
      },
      {
        "claim_id_in_set_A": 5,
        "coverage_percentage_by_set_B": 0
      },
      {
        "claim_id_in_set_A": 6,
        "coverage_percentage_by_set_B": 0
      },
      {
        "claim_id_in_set_A": 7,
        "coverage_percentage_by_set_B": 1
      },
      {
        "claim_id_in_set_A": 8,
        "coverage_percentage_by_set_B": 1
      },
      {
        "claim_id_in_set_A": 9,
        "coverage_percentage_by_set_B": 0.5
      },
      {
        "claim_id_in_set_A": 10,
        "coverage_percentage_by_set_B": 0
      }
    ]
  },
  "answer_source": "omni"
}
```