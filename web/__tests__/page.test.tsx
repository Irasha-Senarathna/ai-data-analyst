import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";

import Home from "../app/page";

afterEach(cleanup);

test("landing page shows the product name", () => {
  render(<Home />);

  expect(
    screen.getByRole("heading", { level: 1, name: /ask your data/i }),
  ).toBeDefined();
});

test("landing page explains that answers come with the SQL used", () => {
  render(<Home />);

  expect(screen.getByText(/shows the sql/i)).toBeDefined();
});
