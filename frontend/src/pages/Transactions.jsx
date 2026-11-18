
import { useState, useEffect } from "react";
import {
  Plus, Search, Trash2, Upload, X, ArrowUpRight,
  ArrowDownRight
} from "lucide-react";
import { transactions as initialTransactions } from "../data/mockData";

const categories = [
  "Food", "Shopping", "Transport", "Bills",
  "Entertainment", "Healthcare", "Other", "Income"
];

const money = (amount) =>
  `₹${Math.abs(amount).toLocaleString("en-IN")}`;

export default function Transactions() {
  const [transactions, setTransactions] = useState(() => {
    try {
      const saved = localStorage.getItem("smartspend_transactions");
      return saved ? JSON.parse(saved) : initialTransactions;
    } catch {
      return initialTransactions;
    }
  });

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    name: "",
    amount: "",
    category: "Food",
    type: "expense",
    date: new Date().toLocaleDateString("en-CA")
  });

  useEffect(() => {
    localStorage.setItem(
      "smartspend_transactions",
      JSON.stringify(transactions)
    );
    window.dispatchEvent(new Event("smartspend:update"));
  }, [transactions]);

  const filtered = transactions.filter((t) => {
    const matchesSearch = t.name
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchesCategory =
      category === "All" || t.category === category;

    return matchesSearch && matchesCategory;
  });

  const income = transactions
    .filter((t) => t.amount > 0)
    .reduce((sum, t) => sum + t.amount, 0);

  const expenses = transactions
    .filter((t) => t.amount < 0)
    .reduce((sum, t) => sum + Math.abs(t.amount), 0);

  function addTransaction(e) {
    e.preventDefault();

    const amount = Number(form.amount);

    if (!form.name.trim() || !Number.isFinite(amount) || amount <= 0) {
      setError("Please enter a valid name and positive amount.");
      return;
    }

    const newTransaction = {
      id: crypto.randomUUID(),
      name: form.name.trim(),
      amount: form.type === "expense" ? -amount : amount,
      category: form.type === "income" ? "Income" : form.category,
      date: form.date
    };

    setTransactions((prev) => [newTransaction, ...prev]);
    setShowModal(false);
    setError("");
    setForm({
      name: "",
      amount: "",
      category: "Food",
      type: "expense",
      date: new Date().toLocaleDateString("en-CA")
    });
  }

  function deleteTransaction(id) {
    if (window.confirm("Delete this transaction?")) {
      setTransactions((prev) => prev.filter((t) => t.id !== id));
    }
  }

  function uploadCSV(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = () => {
      try {
        const text = String(reader.result).replace(/^\uFEFF/, "");
        const lines = text.trim().split(/\r?\n/);
        const headers = lines.shift().split(",").map((h) => h.trim().toLowerCase());

        const required = ["date", "name", "category", "amount"];
        if (!required.every((h) => headers.includes(h))) {
          throw new Error("CSV must contain date,name,category,amount columns.");
        }

        const imported = lines.filter(Boolean).map((line, index) => {
          const values = line.split(",").map((v) => v.trim());
          const row = Object.fromEntries(
            headers.map((h, i) => [h, values[i]])
          );

          const amount = Number(row.amount);
          if (!Number.isFinite(amount) || !row.name || !/^\d{4}-\d{2}-\d{2}$/.test(row.date)) {
            throw new Error(`Invalid data on CSV row ${index + 2}`);
          }

          return {
            id: crypto.randomUUID(),
            name: row.name,
            category: row.category || "Other",
            date: row.date,
            amount
          };
        });

        setTransactions((prev) => [...imported, ...prev]);
        setError("");
        alert(`${imported.length} transactions imported successfully!`);
      } catch (err) {
        setError(err.message);
      }
      event.target.value = "";
    };

    reader.readAsText(file);
  }

  return (
    <div className="space-y-7">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Transactions</h1>
          <p className="text-gray-500 mt-2">
            Manage your income and expenses.
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <label className="flex items-center gap-2 bg-white border border-gray-200 px-4 py-3 rounded-xl cursor-pointer hover:bg-gray-50">
            <Upload size={18} />
            Import CSV
            <input
              type="file"
              accept=".csv,text/csv"
              className="hidden"
              onChange={uploadCSV}
            />
          </label>

          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-3 rounded-xl hover:bg-indigo-700"
          >
            <Plus size={18} />
            Add Transaction
          </button>
        </div>
      </div>

      {error && (
        <div role="alert" className="bg-red-50 text-red-700 p-4 rounded-xl">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {[
          { label: "Total Income", value: income, color: "text-green-600", icon: ArrowUpRight },
          { label: "Total Expenses", value: expenses, color: "text-red-500", icon: ArrowDownRight },
          { label: "Net Balance", value: income - expenses, color: "text-indigo-600", icon: ArrowUpRight }
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
            <div className="flex justify-between items-center">
              <p className="text-gray-500">{label}</p>
              <Icon size={20} className={color} />
            </div>
            <h2 className={`text-2xl font-bold mt-3 ${color}`}>
              {value < 0 ? "-" : ""}{money(value)}
            </h2>
          </div>
        ))}
      </div>

      <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-5 flex flex-wrap gap-4 justify-between">
          <div className="flex items-center gap-3 border border-gray-200 rounded-xl px-4 py-2 w-full sm:w-80">
            <Search size={18} className="text-gray-400" />
            <input
              placeholder="Search transactions..."
              className="outline-none w-full"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="border border-gray-200 rounded-xl px-4 py-2"
          >
            <option value="All">All Categories</option>
            {categories.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left min-w-[650px]">
            <thead className="bg-gray-50 text-gray-500 text-sm">
              <tr>
                <th className="p-4">Transaction</th>
                <th className="p-4">Category</th>
                <th className="p-4">Date</th>
                <th className="p-4">Amount</th>
                <th className="p-4">Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((t) => (
                <tr key={t.id} className="border-t border-gray-100">
                  <td className="p-4 font-medium">{t.name}</td>
                  <td className="p-4">{t.category}</td>
                  <td className="p-4 text-gray-500">{t.date}</td>
                  <td className={`p-4 font-semibold ${t.amount >= 0 ? "text-green-600" : "text-red-500"}`}>
                    {t.amount >= 0 ? "+" : "-"}{money(t.amount)}
                  </td>
                  <td className="p-4">
                    <button
                      onClick={() => deleteTransaction(t.id)}
                      aria-label={`Delete ${t.name}`}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan="5" className="p-10 text-center text-gray-500">
                    No transactions found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-7 w-full max-w-md shadow-xl">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Add Transaction</h2>
              <button onClick={() => setShowModal(false)} aria-label="Close">
                <X size={22} />
              </button>
            </div>

            <form onSubmit={addTransaction} className="space-y-4">
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value })}
                className="w-full border rounded-xl p-3"
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>

              <input
                required
                placeholder="Transaction name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full border rounded-xl p-3"
              />

              <input
                required
                type="number"
                min="0.01"
                step="0.01"
                placeholder="Amount in ₹"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })}
                className="w-full border rounded-xl p-3"
              />

              {form.type === "expense" && (
                <select
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  className="w-full border rounded-xl p-3"
                >
                  {categories.filter((c) => c !== "Income").map((c) => (
                    <option key={c}>{c}</option>
                  ))}
                </select>
              )}

              <input
                required
                type="date"
                value={form.date}
                onChange={(e) => setForm({ ...form, date: e.target.value })}
                className="w-full border rounded-xl p-3"
              />

              <button
                type="submit"
                className="w-full bg-indigo-600 text-white rounded-xl py-3 font-semibold hover:bg-indigo-700"
              >
                Save Transaction
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
