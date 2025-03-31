# Aircraft Engine Component Simulation
#
# This script demonstrates the use of the simulation framework to analyze production and inventory management for a critical aircraft engine component.
#
# Setup and Import

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Import project modules
from src.data_generation.generate_random_data import generate_all_random_data
from src.data_processing.distribution_fitting import (
    analyze_lead_times,
    analyze_demand_patterns
)
from src.models.graph import (
    create_product_structure_graph,
    visualize_graph,
    create_time_space_network
)
from src.simulation.simulation_engine import SimulationEngine
from src.visualization.visualize_results import (
    plot_inventory_levels,
    plot_stock_outs,
    plot_service_level,
    plot_lead_times,
    create_dashboard,
    plot_time_space_events
)

# Set up output directory
output_dir = 'notebook_output'
os.makedirs(output_dir, exist_ok=True)

# Set plotting style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['figure.dpi'] = 100

# -----------------------------------------------------------------------------
# Generate Test Data
#
# For this example, we'll create a simple aircraft engine component supply chain with random data.
# -----------------------------------------------------------------------------

# Generate random data
data = generate_all_random_data(output_dir=os.path.join(output_dir, 'random_data'), num_parts=15)

# Display data samples
print("Part Data Sample:")
print(data['part_df'].head())

print("\nSupply Type Data Sample:")
print(data['supply_type_df'].head())

print("\nBill of Material Sample:")
print(data['bom_df'].head())

# -----------------------------------------------------------------------------
# Create Product Structure Graph
#
# Let's visualize the product structure (Graph 1) to understand the relationships between components.
# -----------------------------------------------------------------------------

# Create product structure graph
product_graph = create_product_structure_graph(data['bom_df'].to_dict('records'))
fig = visualize_graph(product_graph, title="Aircraft Engine Components - Product Structure")
plt.show()

# -----------------------------------------------------------------------------
# Analyze Historical Data
#
# Before running the simulation, let's analyze historical lead times and demand patterns to understand the variability.
# -----------------------------------------------------------------------------

# Analyze lead times
lead_time_results = analyze_lead_times(data['hist_supply_df'])

# Display results for one supplier
if lead_time_results:
    supplier = list(lead_time_results.keys())[0]
    print(f"Lead Time Analysis for {supplier}:")
    print(f"  Mean: {lead_time_results[supplier]['mean']:.2f} days")
    print(f"  Std Dev: {lead_time_results[supplier]['std']:.2f} days")
    print(f"  Best Fit Distribution: {lead_time_results[supplier]['distribution']}")
    # Assuming the figure is a matplotlib figure; if it's not, adjust as needed.
    plt.figure()
    plt.imshow(lead_time_results[supplier]['figure'])
    plt.show()

# Analyze demand patterns
demand_results = analyze_demand_patterns(data['hist_demand_df'])

# Display results for one part
if demand_results:
    part = list(demand_results.keys())[0]
    print(f"Demand Analysis for {part}:")
    print(f"  Mean Monthly Demand: {demand_results[part]['mean_monthly_demand']:.2f} units")
    print(f"  Std Dev: {demand_results[part]['std_monthly_demand']:.2f} units")
    print(f"  Best Fit Distribution: {demand_results[part]['distribution']}")
    plt.figure()
    plt.imshow(demand_results[part]['figure'])
    plt.show()

# -----------------------------------------------------------------------------
# Configure and Run Simulation
#
# Now, let's set up and run the discrete event simulation for 180 days.
# -----------------------------------------------------------------------------

# Initialize simulation engine
simulation = SimulationEngine(
    part_data=data['part_df'],
    supply_type_data=data['supply_type_df'],
    part_source_data=data['part_source_df'],
    bom_data=data['bom_df']
)

# Add initial inventory for all parts
for part in data['part_df']['Name']:
    safety_stock = data['part_df'][data['part_df']['Name'] == part]['SafetyStockQty'].values[0]
    simulation.inventory[part] = safety_stock

# Generate random demand for finished products (Make parts)
make_parts = data['supply_type_df'][data['supply_type_df']['SupplyType'] == 'Make']['Part_Name'].values
for part in make_parts:
    # Generate demand with realistic parameters
    print(f"Adding random demand generation for {part}")
    simulation.env.process(
        simulation.generate_random_demand(
            part=part,
            rate=0.2,  # Approximately one demand every 5 days
            quantity_mean=10,
            quantity_std=3,
            until=180
        )
    )

# Run simulation
print("Running simulation for 180 days...")
simulation.run_simulation(duration=180)
print("Simulation complete!")

# -----------------------------------------------------------------------------
# Analyze Simulation Results
#
# Let's analyze the key metrics from the simulation.
# -----------------------------------------------------------------------------

# Get simulation results
results = simulation.get_results()
metrics = simulation.analyze_results()

# Print key metrics
print("Simulation Metrics:")
print(f"  Total Stock Outs: {metrics['total_stock_outs']}")
print(f"  Service Level: {metrics['service_level']:.2f}%")
print(f"  Average Lead Time: {metrics['avg_lead_time']:.2f} days")
print(f"  Total Production Runs: {metrics['total_production_runs']}")
print(f"  Total Orders Placed: {metrics['total_orders']}")
print(f"  Total Demand: {metrics['total_demand']} units")
print(f"  Total Fulfilled: {metrics['total_fulfilled']} units")
print(f"  Total Backorder: {metrics['total_backorder']} units")

# Display final inventory levels
inventory_df = pd.DataFrame(list(metrics['final_inventory'].items()), columns=['Part', 'Quantity'])
inventory_df = inventory_df.sort_values('Quantity', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='Part', y='Quantity', data=inventory_df)
plt.title('Final Inventory Levels')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# Visualize Results
#
# Let's create various visualizations to understand the simulation results better.
# -----------------------------------------------------------------------------

# Create time-space events visualization
fig = plot_time_space_events(results['events'])
plt.tight_layout()
plt.show()

# Plot inventory levels
fig = plot_inventory_levels(results['events'])
plt.tight_layout()
plt.show()

# Plot service level over time
fig = plot_service_level(results['demands_fulfilled'], groupby='time')
plt.tight_layout()
plt.show()

# Create dashboard
dashboard = create_dashboard(results, figsize=(15, 12))
plt.tight_layout()
plt.show()


# -----------------------------------------------------------------------------
# Scenario Analysis
#
# Let's compare different inventory and supply chain policies.
# -----------------------------------------------------------------------------

def run_scenario(safety_stock_multiplier, demand_rate=0.2, demand_mean=10, demand_std=3, duration=180):
    """Run simulation with modified parameters and return key metrics."""
    # Initialize simulation engine
    simulation = SimulationEngine(
        part_data=data['part_df'],
        supply_type_data=data['supply_type_df'],
        part_source_data=data['part_source_df'],
        bom_data=data['bom_df']
    )

    # Add initial inventory with modified safety stock
    for part in data['part_df']['Name']:
        safety_stock = data['part_df'][data['part_df']['Name'] == part]['SafetyStockQty'].values[0]
        simulation.inventory[part] = safety_stock * safety_stock_multiplier

    # Generate random demand for finished products
    make_parts = data['supply_type_df'][data['supply_type_df']['SupplyType'] == 'Make']['Part_Name'].values
    for part in make_parts:
        simulation.env.process(
            simulation.generate_random_demand(
                part=part,
                rate=demand_rate,
                quantity_mean=demand_mean,
                quantity_std=demand_std,
                until=duration
            )
        )

    # Run simulation
    simulation.run_simulation(duration=duration)

    # Get metrics
    metrics = simulation.analyze_results()

    return metrics


# Run different scenarios
scenarios = {
    'Base Case': run_scenario(safety_stock_multiplier=1.0),
    'High Safety Stock': run_scenario(safety_stock_multiplier=2.0),
    'Low Safety Stock': run_scenario(safety_stock_multiplier=0.5),
    'High Demand': run_scenario(safety_stock_multiplier=1.0, demand_rate=0.3, demand_mean=15),
    'Low Demand': run_scenario(safety_stock_multiplier=1.0, demand_rate=0.1, demand_mean=5)
}

# Compare service levels
service_levels = {scenario: metrics['service_level'] for scenario, metrics in scenarios.items()}
plt.figure(figsize=(10, 6))
plt.bar(list(service_levels.keys()), list(service_levels.values()))
plt.title('Service Level Comparison Across Scenarios')
plt.ylabel('Service Level (%)')
plt.ylim(0, 100)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Compare stock outs
stock_outs = {scenario: metrics['total_stock_outs'] for scenario, metrics in scenarios.items()}
plt.figure(figsize=(10, 6))
plt.bar(list(stock_outs.keys()), list(stock_outs.values()))
plt.title('Stock Out Events Comparison Across Scenarios')
plt.ylabel('Number of Stock Outs')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# Conclusion
#
# Based on the simulation results, we can draw the following conclusions:
#
# 1. Service Level Impact: Higher safety stock levels significantly improve service levels but come with additional inventory costs.
# 2. Stock Out Events: Low safety stock policies lead to more frequent stock outs, particularly during periods of high demand.
# 3. Lead Time Variability: Supplier lead time variability has a significant impact on stock out risk. Working with suppliers to reduce this variability could improve overall performance.
# 4. Production Scheduling: Better coordination between production and inventory management can reduce the number of emergency production runs.
# 5. Recommendations:
#    - Implement a more sophisticated inventory policy that dynamically adjusts safety stock levels based on demand forecasts.
#    - Focus on reducing lead time variability with key suppliers.
#    - Consider implementing a more proactive production scheduling approach.
#
# Next steps would involve further refining the model with real data and testing more sophisticated inventory and production policies.
# -----------------------------------------------------------------------------