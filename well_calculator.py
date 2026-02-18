import math

def arps_rate(qi, Di, b, t):
	"""Return production rate at time t (months) using Arps hyperbolic form.
	qi: initial monthly rate (same units as output)
	Di: initial decline (per month)
	b: hyperbolic b factor
	t: time in months
	"""
	if b == 0:
		return qi * math.exp(-Di * t)
	return qi / ((1 + b * Di * t) ** (1.0 / b))


print("Enter oil inputs:")
oil_qi = float(input("Starting oil production (barrels per month) [e.g. 3000]: "))
oil_price = float(input("Oil price ($/bbl): "))
oil_b = float(input("Oil hyperbolic b parameter (0 for exponential) [e.g. 0.5]: "))
oil_D_annual_pct = float(input("Oil initial decline (% per year) [e.g. 30]: "))

print("\nEnter gas inputs (or 0 to skip):")
gas_qi = float(input("Starting gas production (MCF per month) [e.g. 10000]: "))
gas_price = float(input("Gas price ($/MCF): "))
gas_b = float(input("Gas hyperbolic b parameter (0 for exponential) [e.g. 0.3]: "))
gas_D_annual_pct = float(input("Gas initial decline (% per year) [e.g. 40]: "))

operating_cost = float(input("Monthly operating cost? $"))
drill_cost = float(input("Total drilling cost? $"))
months = int(input("Months to simulate [e.g. 60]: "))

# convert annual % to decimal per month (approximate by dividing by 12)
oil_D = (oil_D_annual_pct / 100.0) / 12.0
gas_D = (gas_D_annual_pct / 100.0) / 12.0

monthly_oil = []
monthly_gas = []
monthly_revenue = []
monthly_profit = []

for m in range(months):
	t = m  # months since start
	qo = arps_rate(oil_qi, oil_D, oil_b, t) if oil_qi > 0 else 0.0
	qg = arps_rate(gas_qi, gas_D, gas_b, t) if gas_qi > 0 else 0.0
	rev = qo * oil_price + qg * gas_price
	profit = rev - operating_cost
	monthly_oil.append(qo)
	monthly_gas.append(qg)
	monthly_revenue.append(rev)
	monthly_profit.append(profit)

cum_oil = sum(monthly_oil)
cum_gas = sum(monthly_gas)
cum_revenue = sum(monthly_revenue)
cum_profit = sum(monthly_profit) - drill_cost  # include drill cost upfront

avg_monthly_profit = sum(monthly_profit) / months
payback_month = None
running = -drill_cost
for i, p in enumerate(monthly_profit, start=1):
	running += p
	if running >= 0:
		payback_month = i
		break

print("\n--- Simulation Results ---")
print(f"Months simulated: {months}")
print(f"Cumulative oil produced: {cum_oil:,.1f} bbl")
print(f"Cumulative gas produced: {cum_gas:,.1f} MCF")
print(f"Cumulative revenue: ${cum_revenue:,.2f}")
print(f"Cumulative NPV-like profit (incl drill cost): ${cum_profit:,.2f}")
print(f"Average monthly profit: ${avg_monthly_profit:,.2f}")
if payback_month:
	print(f"Payback period: {payback_month} months")
else:
	print("Payback period: not achieved within simulation window")

print("\n--- First 12 months (monthly oil bbl / gas MCF / revenue / profit) ---")
for i in range(min(12, months)):
	print(f"M{i+1:02d}: {monthly_oil[i]:,.1f} / {monthly_gas[i]:,.1f} -> ${monthly_revenue[i]:,.2f} / ${monthly_profit[i]:,.2f}")
