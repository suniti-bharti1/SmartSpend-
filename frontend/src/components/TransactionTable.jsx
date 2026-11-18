
import { useTransactions } from "../hooks/useFinance";

export default function TransactionTable() {
  const transactions = useTransactions().slice().sort((a,b)=>String(b.date).localeCompare(String(a.date))).slice(0,6);
  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
      <h3 className="text-lg font-semibold mb-5">
        Recent Transactions
      </h3>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="text-gray-500 border-b border-gray-100">
              <th className="py-3">Transaction</th>
              <th>Category</th>
              <th>Date</th>
              <th className="text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((transaction) => (
              <tr key={transaction.id} className="border-b border-gray-50">
                <td className="py-4 font-medium">{transaction.name}</td>
                <td>{transaction.category}</td>
                <td className="text-gray-500">{transaction.date}</td>
                <td
                  className={`text-right font-semibold ${
                    transaction.amount > 0 ? "text-green-600" : "text-red-500"
                  }`}
                >
                  {transaction.amount > 0 ? "+" : "-"}₹
                  {Math.abs(transaction.amount).toLocaleString("en-IN")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
