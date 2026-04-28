export const calculateScore = (skill) => {
  const { demand, growth, difficulty } = skill;
  return (0.6 * growth) + (0.3 * demand) - (0.1 * difficulty);
};
