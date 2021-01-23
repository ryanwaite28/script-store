/**
 * Ryan M. Waite
 * https://www.linkedin.com/in/ryanwaite28/
 * https://github.com/ryanwaite28
 * https://stackoverflow.com/users/story/5632252
 * 
 * Hello World!
 *
 * So, i have a feeling that i failed a facebook interview i had on 1/22/2021.
 * The question i was given is in the other comment below.
 *
 * I am guessing they think i'm not "experienced/good enough" because
 * i didn't get the answer that they are looking for in a LIMITED time frame.
 *
 * I understand computer science.
 * 
 * i think i am better at the theory of it than the practice, or at least equally adept in both.
 *
 * This is my problem with coding interviews:
 *
 * I think it is too dismissive/devoid of determination and potential.
 * 
 * I get that a company wants someone who is competent and need these coding exercises
 * to vet out those who are seriously not equiped for the job; i know how important computational thinking is.
 * But to give someone a RANDOM question and expect them to figure it out in a 30-minute interview, that is where i have questions.
 * - Do you want them to actually get the answer and in the BEST way?
 * - Are you just guaging their understanding of data structures and algorithms?
 * - Do you think 30 minutes is enough to find the BEST solution to said RANDOM problem?
 *
 * It takes time to think about stuff, especially if you are trying to do it in the BEST way.
 * I don't know how someone can get the best when not given a fair amount of time.
 * It's as if company aren't willing to give someone, with potential, soft-skills and a solid starting point that an organization can work with, a chance.
 * I don't know, maybe i'm just complaining.
 *
 * BUT, here are my two goals (hopefully become vows) to myself:
 * - i will not apply to another job in my life.
 * - Whatever i learn, i will share it back to the world to help whoever may need it.
 * - I will start something of my own for myself and other; something beneficial to the world.
 *
 * Call it petty, but whatever question i get on a coding interview, i'll share my answer once i get it working.
 * 
 * Anyways, Happy Coding.
*/


/*
// ==Question==

// Given a sequence of integers and an integer total target, return whether a contiguous sequence of integers sums up to target.

// ===Example===

// [1, 3, 1, 4, 23], 8 : True (because 3 + 1 + 4 = 8)
// [1, 3, 1, 4, 23], -9 : False
*/

// my working solution. oh well
function isContiguous(nums, target) {
  // find all combinations of the list
  // https://stackoverflow.com/questions/5752002/find-all-possible-subset-combos-in-an-array
  // https://codereview.stackexchange.com/questions/7001/generating-all-combinations-of-an-array
  
  const combos = new Array(1 << nums.length)
    .fill()
    .map((e1, i) => {
      const combo = nums.filter((e2, j) => i & 1 << j);
      return combo;
    });

  // check each combo if they sum to target
  for (const l of combos) {
    let sum = l.reduce((a, b) => a + b, 0);
    if (sum === target) {
      return true;
    }
  }

  return false;
}