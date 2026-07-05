export default function Loading() {
  return (
    <div className="container flex min-h-screen flex-col gap-8 pt-32">
      <div className="shimmer h-12 w-2/3 rounded-2xl bg-coffee/40" />
      <div className="shimmer h-6 w-1/2 rounded-xl bg-coffee/40" />
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="shimmer h-72 rounded-3xl bg-coffee/40"
          />
        ))}
      </div>
    </div>
  );
}
