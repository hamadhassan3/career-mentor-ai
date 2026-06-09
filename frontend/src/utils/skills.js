// Format a skill (or language) label for display only — the stored value is
// never changed. Turns snake_case predictions ("machine_learning") into spaced
// words and capitalizes the first letter of each all-lowercase word, so soft
// skills that come back lowercase ("communication") render as "Communication",
// while acronyms and intentional casing ("iOS", "SQL", "JavaScript") are left
// untouched.
export const formatSkill = (skill) => {
  if (typeof skill !== 'string') return skill;
  return skill
    .replace(/_/g, ' ')
    .split(' ')
    .map((word) =>
      word === word.toLowerCase()
        ? word.charAt(0).toUpperCase() + word.slice(1)
        : word
    )
    .join(' ');
};
