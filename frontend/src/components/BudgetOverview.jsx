
import { useBudgets, useTransactions } from "../hooks/useFinance";

export default function BudgetOverview() {
  const budgets = useBudgets();
  const transactions = useTransactions();
  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
      <h3 className="text-lg font-semibold mb-6">Budget Overview</h3>

      <div className="space-y-6">
        {budgets.map((budget) => {
          const spent = transactions.filter(t=>t.amount<0 && t.category?.toLowerCase()===budget.category.toLowerCase()).reduce((a,t)=>a-t.amount,0);
          const percent = budget.limit ? (spent / budget.limit) * 100 : 0;

          return (
            <div key={budget.category}>
              <div className="flex justify-between mb-2 text-sm">
                <span className="font-medium">{budget.category}</span>
                <span className="text-gray-500">
                  ₹{spent.toLocaleString("en-IN")} / ₹
                  {budget.limit.toLocaleString("en-IN")}
                </span>
              </div>

              <div className="w-full bg-gray-100 rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full ${
                    percent >= 90 ? "bg-red-500" : "bg-indigo-500"
                  }`}
                  style={{ width: `${Math.min(percent, 100)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
