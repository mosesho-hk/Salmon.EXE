import math

import pulp

def optimize_purchasing_schedule(
    maximum_budget: float, 
    buyer_demand_kg: float, 
    deadline_days: int, 
    supplier_offer_price_kg: list, 
    supplier_saleable_stock_kg: list,
    *,
    period_labels: list | None = None,
):
    """
    Optimizes purchasing schedule under deterministic budget and quantity constraints.
    """
    
    if isinstance(deadline_days, bool) or not isinstance(deadline_days, int):
        raise ValueError("The deadline must be a positive integer number of time steps.")
    if deadline_days < 1 or deadline_days > min(len(supplier_offer_price_kg), len(supplier_saleable_stock_kg)):
        raise ValueError("The deadline must fit within the supplied price and stock data.")
    if period_labels is not None and len(period_labels) < deadline_days:
        raise ValueError("A label is required for every time step within the deadline.")
    # Slice the horizon to match the deadline window
    prices = supplier_offer_price_kg[:deadline_days]
    stocks = supplier_saleable_stock_kg[:deadline_days]
    days = range(len(prices))

    for name, values in (
        ("budget", [maximum_budget]), ("demand", [buyer_demand_kg]),
        ("prices", prices), ("stock", stocks),
    ):
        if any(isinstance(value, bool) or not isinstance(value, (int, float))
               or not math.isfinite(value) or value < 0 for value in values):
            raise ValueError(f"All {name} values must be finite, non-negative numbers.")

    # For divisible purchases, cheapest-first gives the exact minimum cost.
    # Diagnose infeasible inputs before asking the solver for a schedule.
    available = math.fsum(stocks)
    if available < buyer_demand_kg:
        raise ValueError(
            f"Insufficient stock within the deadline: need {buyer_demand_kg:.2f} kg, "
            f"available {available:.2f} kg (shortfall {buyer_demand_kg - available:.2f} kg)."
        )
    remaining = buyer_demand_kg
    costs = []
    for index in sorted(days, key=lambda index: prices[index]):
        quantity = min(remaining, stocks[index])
        costs.append(quantity * prices[index])
        remaining -= quantity
        if remaining <= 0:
            break
    minimum_cost = math.fsum(costs)
    if minimum_cost > maximum_budget + 1e-7:
        raise ValueError(
            f"Insufficient budget: minimum cost is {minimum_cost:.2f}, "
            f"budget is {maximum_budget:.2f} "
            f"(shortfall {minimum_cost - maximum_budget:.2f}, in the input price currency; "
            "NOK for forecast data)."
        )
    if buyer_demand_kg == 0:
        return []
    
    # 1. Initialize the Optimization Problem (Minimize Total Acquisition Cost)
    model = pulp.LpProblem("Deterministic_Purchase_Optimization", pulp.LpMinimize)
    
    # 2. Decision Variables: Quantity to purchase at each time step t
    x = [model.add_variable(f"Day_{t+1}_qty", lowBound=0, cat='Continuous') for t in days]
    
    # 3. Objective Function: Minimize sum of (Price * Quantity)
    model += pulp.lpSum(prices[t] * x[t] for t in days), "Total_Acquisition_Cost"
    
    # 4. Constraints
    # Constraint A: Meet the exact buyer demand by the deadline
    model += pulp.lpSum(x[t] for t in days) == buyer_demand_kg, "Demand_Fulfillment_Constraint"
    
    # Constraint B: Total expenditure cannot exceed the maximum budget
    model += pulp.lpSum(prices[t] * x[t] for t in days) <= maximum_budget, "Budget_Ceiling_Constraint"
    
    # Constraint C: Purchases at each time step cannot exceed available saleable stock
    for t in days:
        model += x[t] <= stocks[t], f"Stock_Capacity_Constraint_Day_{t+1}"
        
    # 5. Solve the optimization problem
    solver = pulp.HiGHS(msg=False)
    if not solver.available():
        raise RuntimeError(
            "The HiGHS solver is missing. Install the project dependencies with "
            "python -m pip install -r requirements.txt"
        )
    result = model.solve(solver)
    
    # 6. Extract and format the results into the required output list
    schedule = []
    if result.status == pulp.LpSolveStatus.Optimal:
        for t in days:
            qty = x[t].varValue
            if qty > 1e-5:  # Filter out near-zero floating-point allocations
                budget_allocated = qty * prices[t]
                when_to_buy = period_labels[t] if period_labels is not None else f"Day {t+1}"
                schedule.append((when_to_buy, round(budget_allocated, 2), round(qty, 2)))
        return schedule
    else:
        raise RuntimeError(
            f"Solver returned {result.status.name} despite feasible inputs "
            f"(minimum cost {minimum_cost:.2f}, budget {maximum_budget:.2f}). "
            "Check the Python environment and installed PuLP/HiGHS versions."
        )

# --- Example Execution ---
if __name__ == "__main__":
    # Define inputs matching your schema specifications
    maximum_budget = 1400.0               # £1,400 max budget
    buyer_demand_kg = 100.0              # 100 kg required
    deadline_days = 5                     # 5-day deadline window
    
    # Daily parameters across the 5-day horizon
    supplier_offer_price_kg = [15.5, 14.0, 16.2, 13.5, 14.5]  #[cite: 1]
    supplier_saleable_stock_kg = [40.0, 50.0, 30.0, 60.0, 40.0] #[cite: 1]
    
    try:
        execution_plan = optimize_purchasing_schedule(
            maximum_budget=maximum_budget,
            buyer_demand_kg=buyer_demand_kg,
            deadline_days=deadline_days,
            supplier_offer_price_kg=supplier_offer_price_kg,
            supplier_saleable_stock_kg=supplier_saleable_stock_kg
        )
        
        print("Optimized Purchase Schedule (when_to_buy, budget, quantity):")
        for item in execution_plan:
            print(f"When to buy: {item[0]} | Budget Allocated: £{item[1]:.2f} | Quantity: {item[2]} kg")
            
    except (ValueError, RuntimeError) as e:
        print(f"Optimization Error: {e}")
