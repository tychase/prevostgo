export default function CoachCard({ coach }) {
  const model = coach.specs?.model ?? "—";
  const chassis = coach.specs?.chassis_type ?? "—";
  const mileage = coach.specs?.mileage;
  const slides = coach.specs?.slide_count;

  return (
    <article className="rounded-2xl overflow-hidden bg-slate-900">
      <img src={coach.heroImageUrl} className="w-full h-56 object-cover" alt="" />
      <div className="p-4">
        <h3 className="text-lg font-semibold line-clamp-2">{coach.title}</h3>
        <div className="mt-1 text-amber-400 font-semibold">
          {coach.price != null ? `$${coach.price.toLocaleString()}` : "Contact for Price"}
        </div>
        <div className="mt-2 text-sm opacity-80 flex gap-3">
          <span>{coach.year ?? "—"}</span>
          <span>• {model}</span>
          <span>• Chassis: {chassis}</span>
        </div>
        <div className="mt-1 text-xs opacity-70 flex gap-3">
          <span>{mileage != null ? `${mileage.toLocaleString()} mi` : "Mileage: —"}</span>
          <span>{slides != null ? `${slides} Slide${slides===1?"":"s"}` : "Slides: —"}</span>
        </div>
      </div>
    </article>
  );
}