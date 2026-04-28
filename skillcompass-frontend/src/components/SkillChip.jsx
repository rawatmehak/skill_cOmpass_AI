export default function SkillChip({ name, type = "have" }) {
  const base = "px-3 py-1 rounded-full text-sm font-medium mr-2 mb-2 inline-block";
  const haveStyle = "bg-green-100 text-green-800";
  const missingStyle = "bg-red-100 text-red-800";
  return (
    <span className={`${base} ${type === "have" ? haveStyle : missingStyle}`}>
      {name}
    </span>
  );
}
