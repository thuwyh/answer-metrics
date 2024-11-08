# question
from metrics import compare_with_gold_answer


question = "What were the key outcomes and voter trends in the 2024 Oklahoma elections?"
# first, extract top_level_key_points and their supporting_key_points
gold_answer = [
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
]

# answer to evaluate
other_answer = """In the 2024 Oklahoma elections, Donald Trump won the state with 66.17% of the vote, maintaining Oklahoma's Republican dominance [[1](https://www.pryorinfopub.com/news/oklahoma-election-recap-high-turnout-big-wins-and-key-decisions/article_c5b190ba-9c41-11ef-b49c-d3bc938bab21.html)]. Despite a record number of registered voters, Oklahoma experienced the lowest voter turnout in the nation, with only 53% of eligible voters participating, marking a decline from previous presidential elections [[2](https://oklahomavoice.com/2024/11/06/oklahoma-voter-turnout-lowest-in-the-nation-drops-from-previous-presidential-elections/)],[[3](https://www.oklahoman.com/story/news/politics/2024/11/06/election-results-oklahoma-voter-turnout-in-fell-in-2024/76089629007/)].

- **Voter Registration and Turnout**: Oklahoma had a record 2.4 million registered voters, but turnout was only 64% among registered voters, a decrease from 69% in 2020 [[2](https://oklahomavoice.com/2024/11/06/oklahoma-voter-turnout-lowest-in-the-nation-drops-from-previous-presidential-elections/)],[[3](https://www.oklahoman.com/story/news/politics/2024/11/06/election-results-oklahoma-voter-turnout-in-fell-in-2024/76089629007/)].
- **State Elections**: Republicans retained their supermajority in the state Senate, winning several key races [[4](https://www.oklahoman.com/story/news/politics/elections/2024/11/05/oklahoma-senate-election-2024-results/75988381007/)].
- **Ballot Measures**: Oklahoma voters passed State Question 834 overwhelmingly, while State Question 833 failed [[1](https://www.pryorinfopub.com/news/oklahoma-election-recap-high-turnout-big-wins-and-key-decisions/article_c5b190ba-9c41-11ef-b49c-d3bc938bab21.html)].

The election highlighted Oklahoma's consistent support for Republican candidates and revealed a trend of low voter engagement despite high registration numbers and early voting participation.
"""

result = compare_with_gold_answer(question,
                                  gold_answer,
                                  other_answer)

print(result)