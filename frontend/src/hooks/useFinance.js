import { useState, useEffect } from "react";
import { transactions as defaults } from "../data/mockData";
export const currency = (n) => `₹${Number(n || 0).toLocaleString("en-IN", {maximumFractionDigits: 2})}`;
export function useTransactions() {
 const read = () => { try { const v=JSON.parse(localStorage.getItem("smartspend_transactions")); return Array.isArray(v)?v:defaults; } catch {return defaults;} };
 const [items,setItems]=useState(read);
 useEffect(()=>{ const sync=()=>setItems(read()); window.addEventListener("smartspend:update",sync); window.addEventListener("storage",sync); return ()=>{window.removeEventListener("smartspend:update",sync);window.removeEventListener("storage",sync)};},[]);
 return items;
}
export function useBudgets() {
 const [items,setItems]=useState(()=>{try {return JSON.parse(localStorage.getItem("smartspend_budgets")) || []}catch{return []}});
 useEffect(()=>{const sync=()=>{try{setItems(JSON.parse(localStorage.getItem("smartspend_budgets"))||[])}catch{setItems([])}};window.addEventListener("smartspend:update",sync);window.addEventListener("storage",sync);return()=>{window.removeEventListener("smartspend:update",sync);window.removeEventListener("storage",sync)}},[]);
 return items;
}
export function summarize(items) {const income=items.filter(t=>t.amount>0).reduce((s,t)=>s+Number(t.amount),0);const expenses=items.filter(t=>t.amount<0).reduce((s,t)=>s-Math.min(0,Number(t.amount)),0);return {income,expenses,savings:income-expenses,rate:income?((income-expenses)/income)*100:0};}
