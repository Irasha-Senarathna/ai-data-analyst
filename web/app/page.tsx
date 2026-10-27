const EXAMPLE_QUESTIONS = [
  "What was total revenue in 2017?",
  "Which product categories grew fastest last quarter?",
  "Why did revenue drop in December 2017?",
  "Do rainy days change order volume in São Paulo?",
];

const STEPS = [
  { title: "Understand", text: "Reads your question and the governed metric definitions." },
  { title: "Query", text: "Writes read-only SQL, checks it, and runs it on the warehouse." },
  { title: "Explain", text: "Answers in plain English, draws a chart, and includes the query." },
];

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-12 px-4 py-16 sm:px-8 sm:py-24">
      <header className="flex flex-col gap-4">
        <p className="text-sm font-medium uppercase tracking-wide text-zinc-500">AI Data Analyst</p>
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Ask your data</h1>
        <p className="max-w-xl text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          Ask a business question in plain English. The analyst finds the right tables, runs a
          safe query, and shows the SQL behind every answer.
        </p>
      </header>

      <section aria-labelledby="how-heading" className="flex flex-col gap-4">
        <h2 id="how-heading" className="text-xl font-semibold">
          How it works
        </h2>
        <ol className="grid gap-4 sm:grid-cols-3">
          {STEPS.map((step, index) => (
            <li
              key={step.title}
              className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800"
            >
              <p className="text-sm text-zinc-500">Step {index + 1}</p>
              <p className="font-medium">{step.title}</p>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{step.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="examples-heading" className="flex flex-col gap-4">
        <h2 id="examples-heading" className="text-xl font-semibold">
          Questions you will be able to ask
        </h2>
        <ul className="flex flex-col gap-2">
          {EXAMPLE_QUESTIONS.map((question) => (
            <li
              key={question}
              className="rounded-md bg-zinc-100 px-4 py-3 text-zinc-800 dark:bg-zinc-900 dark:text-zinc-200"
            >
              {question}
            </li>
          ))}
        </ul>
        <p className="text-sm text-zinc-500">The chat is coming in milestone 8.</p>
      </section>
    </main>
  );
}
