import { useTransactions } from "../hooks/useFinance";

import { useState, useEffect } from "react";
import { Plus, Wallet, AlertTriangle, Pencil, Trash2 } from "lucide-react";
import { budgets as initialBudgets } from "../data/mockData";

export default function Budgets() {
  const transactions = useTransactions();
  const [budgets, setBudgets] = useState(() => {
    try {
      const saved = localStorage.getItem("smartspend_budgets");
      return saved ? JSON.parse(saved) : initialBudgets;
    } catch {
      return initialBudgets;
    }
  });

  const [category, setCategory] = useState("");
  const [limit, setLimit] = useState("");
  const [editing, setEditing] = useState(null);

  useEffect(() => {
    localStorage.setItem("smartspend_budgets", JSON.stringify(budgets));
    window.dispatchEvent(new Event("smartspend:update"));
  }, [budgets]);

  const spendFor = (category) => transactions.filter(t => t.amount < 0 && t.category?.toLowerCase() === category.toLowerCase()).reduce((sum,t) => sum - t.amount,0);
  const totalBudget = budgets.reduce((sum, b) => sum + b.limit, 0);
  const totalSpent = budgets.reduce((sum, b) => sum + spendFor(b.category), 0);

  function saveBudget(e) {
    e.preventDefault();

    const amount = Number(limit);
    if (!category.trim() || !Number.isFinite(amount) || amount <= 0) {
      alert("Enter a valid category and positive budget amount.");
      return;
    }

    if (editing !== null) {
      setBudgets((prev) =>
        prev.map((b, i) =>
          i === editing ? { ...b, category: category.trim(), limit: amount } : b
        )
      );
    } else {
      if (budgets.some((b) => b.category.toLowerCase() === category.trim().toLowerCase())) {
        alert("A budget already exists for this category.");
        return;
      }
      setBudgets((prev) => [
        ...prev,
        { category: category.trim(), spent: 0, limit: amount }
      ]);
    }

    setCategory("");
    setLimit("");
    setEditing(null);
  }

  function editBudget(index) {
    setEditing(index);
    setCategory(budgets[index].category);
    setLimit(String(budgets[index].limit));
  }

  function deleteBudget(index) {
    setBudgets((prev) => prev.filter((_, i) => i !== index));
    setEditing(null);
    setCategory("");
    setLimit("");
  }

  return (
    <div className="space-y-7">
      <div>
        <h1 className="text-3xl font-bold">Budget Management</h1>
        <p className="text-gray-500 mt-2">
          Plan your spending and track your monthly limits.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {[
          { label: "Total Budget", value: totalBudget, color: "text-indigo-600" },
          { label: "Total Spent", value: totalSpent, color: "text-red-500" },
          { label: "Remaining Budget", value: totalBudget - totalSpent, color: "text-green-600" }
        ].map((item) => (
          <div key={item.label} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
            <div className="flex items-center gap-2 text-gray-500">
              <Wallet size={18} />
              {item.label}
            </div>
            <h2 className={`text-2xl font-bold mt-3 ${item.color}`}>
              {item.value < 0 ? "-" : ""}₹{Math.abs(item.value).toLocaleString("en-IN")}
            </h2>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm lg:col-span-1">
          <h2 className="text-xl font-semibold mb-5">
            {editing !== null ? "Edit Budget" : "Add New Budget"}
          </h2>

          <form onSubmit={saveBudget} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Category</label>
              <input
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g. Food"
                className="w-full border border-gray-200 rounded-xl p-3"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Monthly Limit (₹)</label>
              <input
                type="number"
                min="1"
                value={limit}
                onChange={(e) => setLimit(e.target.value)}
                placeholder="e.g. 8000"
                className="w-full border border-gray-200 rounded-xl p-3"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full bg-indigo-600 text-white rounded-xl py-3 flex justify-center items-center gap-2 hover:bg-indigo-700"
            >
              <Plus size={18} />
              {editing !== null ? "Update Budget" : "Add Budget"}
            </button>

            {editing !== null && (
              <button
                type="button"
                onClick={() => {
                  setEditing(null);
                  setCategory("");
                  setLimit("");
                }}
                className="w-full border rounded-xl py-3"
              >
                Cancel Editing
              </button>
            )}
          </form>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {budgets.map((budget, index) => {
            const spent = spendFor(budget.category);
            const percent = budget.limit > 0
              ? (spent / budget.limit) * 100
              : 0;

            return (
              <div key={budget.category} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-semibold text-lg">{budget.category}</h3>

                  <div className="flex gap-3">
                    <button onClick={() => editBudget(index)} aria-label="Edit budget" className="text-indigo-600">
                      <Pencil size={18} />
                    </button>
                    <button onClick={() => deleteBudget(index)} aria-label="Delete budget" className="text-red-500">
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>

                <div className="flex justify-between text-sm mb-3">
                  <span>₹{spent.toLocaleString("en-IN")} spent</span>
                  <span>₹{budget.limit.toLocaleString("en-IN")} limit</span>
                </div>

                <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      percent >= 100
                        ? "bg-red-500"
                        : percent >= 80
                        ? "bg-amber-500"
                        : "bg-indigo-500"
                    }`}
                    style={{ width: `${Math.min(percent, 100)}%` }}
                  />
                </div>

                <p className="text-sm text-gray-500 mt-2">
                  {percent.toFixed(1)}% used
                </p>

                {percent >= 80 && (
                  <p className="flex items-center gap-2 text-amber-600 text-sm mt-3">
                    <AlertTriangle size={16} />
                    {percent >= 100
                      ? "Budget exceeded!"
                      : "You are approaching your budget limit."}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
