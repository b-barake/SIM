import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

def generate_part_data(num_parts=20):
    """
    Generate random part data.

    Parameters:
    -----------
    num_parts : int
        Number of parts to generate.

    Returns:
    --------
    part_df : pandas.DataFrame
        Dataframe containing part data.
    """

    # Generate part names (P001, P002, ...)
    part_names = [f"P{i:03d}" for i in range(1, num_parts+1)]

    # Generate random sites (S1, S2, S3)
    sites = [f"S{random.randint(1, 3)}" for _ in range(num_parts)]

    # Generate random data for other columns
    avg_qty = np.random.randint(10, 100, size=num_parts)
    safety_lead_time = np.random.randint(1, 10, size=num_parts)
    safety_stock_qty = np.random.randint(5, 50, size=num_parts)
    unit_of_measure = np.random.choice(['EA', 'LB', 'KG'], size=num_parts)

    # Create dataframe
    part_df = pd.DataFrame({
        'Name': part_names,
        'Site': sites,
        'AverageQty': avg_qty,
        'SafetyLeadTime': safety_lead_time,
        'SafetyStockQty': safety_stock_qty,
        'UnitOfMeasure': unit_of_measure
    })

    return part_df

def generate_supply_type_data(part_df):
    """
    Generate random supply type data.

    Parameters:
    -----------
    part_df : pandas.DataFrame
        Dataframe containing part data.

    Returns:
    --------
    supply_type_df : pandas.DataFrame
        Dataframe containing supply type data.
    """

    part_names = part_df['Name'].tolist()

    # Randomly assign supply types (35% Make, 65% Buy)
    supply_types = np.random.choice(['Make', 'Buy'],
                                    size=len(part_names),
                                    p=[0.35, 0.65])

    # Create dataframe
    supply_type_df = pd.DataFrame({
        'Part_Name': part_names,
        'SupplyType': supply_types
    })

    return supply_type_df


def generate_part_source_data(supply_type_df):
    """
    Generate random part source data for Buy parts.

    Parameters:
    -----------
    supply_type_df : pandas.DataFrame
        Dataframe containing supply type data.

    Returns:
    --------
    part_source_df : pandas.DataFrame
        Dataframe containing part source data.
    """

    # Get Buy parts
    buy_parts = supply_type_df[supply_type_df['SupplyType'] == 'Buy']['Part_Name'].tolist()

    # Generate random data
    part_names = []
    sources = []
    lead_times = []

    for part in buy_parts:
        # Each buy part can have 1-3 suppliers
        num_suppliers = random.randint(1, 3)
        for i in range(num_suppliers):
            part_names.append(part)
            sources.append(f"Supplier_{random.randint(1, 10)}")
            lead_times.append(random.randint(5, 30))

    # Create dataframe
    part_source_df = pd.DataFrame({
        'Part_Name': part_names,
        'SupplyType': 'Buy',
        'Source': sources,
        'EffLeadTime': lead_times
    })

    return part_source_df

# def generate_bom_data(supply_type_df):
#     """
#     Generate random Bill of Material (BOM) data for Make parts.
#
#     Parameters:
#     -----------
#     supply_type_df : pandas.DataFrame
#         Dataframe containing supply type data.
#
#     Returns:
#     --------
#     bom_df : pandas.DataFrame
#         Dataframe containing BOM data
#     """
#
#     # Get Make parts (assemblies)
#     make_parts = supply_type_df[supply_type_df['SupplyType'] == 'Make']['Part_Name'].tolist()
#
#     # Get all parts (potential components)
#     all_parts = supply_type_df['Part_Name'].tolist()
#
#     # Generate random BOM data
#     assemblies = []
#     components = []
#     qty_per = []
#     scrap = []
#
#     for assembly in make_parts:
#         # Each assembly uses 2-5 components
#         num_components = random.randint(2, 5)
#         # Sample components without replacement (no duplicates)
#         selected_components = random.sample(
#             [p for p in all_parts if p != assembly],
#             min(num_components, len(all_parts) - 1)
#         )
#
#         for component in selected_components:
#             assemblies.append(assembly)
#             components.append(component)
#             qty_per.append(random.randint(1, 10))
#             scrap.append(round(random.uniform(0, 0.15), 2)) # 0-15% scrap
#
#     # Create dataframe
#     bom_df = pd.DataFrame({
#         'Assembly': assemblies,
#         'Component': components,
#         'QuantityPer': qty_per,
#         'Scrap': scrap
#     })
#
#     return bom_df

def generate_bom_data(supply_type_df):
    """
    Generate hierarchical Bill of Material (BOM) data with a single root assembly.
    The structure ensures all parts are used and organized in a proper hierarchy.

    Parameters:
    -----------
    supply_type_df : pandas.DataFrame
        Dataframe containing supply type data with Part_Name and SupplyType columns.

    Returns:
    --------
    bom_df : pandas.DataFrame
        Dataframe containing hierarchical BOM data with a single root assembly.
    """
    import random

    # Get Make parts (assemblies)
    make_parts = supply_type_df[supply_type_df['SupplyType'] == 'Make']['Part_Name'].tolist()

    if not make_parts:
        raise ValueError("No 'Make' parts found in supply type data.")

    # Get all parts (potential components)
    all_parts = supply_type_df['Part_Name'].tolist()

    # 1. Randomly choose a root node from Make parts
    root_assembly = random.choice(make_parts)

    # Remove root from regular assemblies list
    regular_assemblies = [p for p in make_parts if p != root_assembly]

    # Track which parts have been used as components
    used_components = set()

    # Generate random BOM data
    assemblies = []
    components = []
    qty_per = []
    scrap = []

    # First, create BOM entries for regular assemblies
    for assembly in regular_assemblies:
        # Each assembly uses 2-5 components
        num_components = random.randint(2, 5)
        # Sample components without replacement (no duplicates)
        available_components = [p for p in all_parts if p != assembly and p != root_assembly]

        selected_components = random.sample(
            available_components,
            min(num_components, len(available_components))
        )

        for component in selected_components:
            assemblies.append(assembly)
            components.append(component)
            qty_per.append(random.randint(1, 10))
            scrap.append(round(random.uniform(0, 0.15), 2))  # 0-15% scrap

            # Mark this component as used
            used_components.add(component)

    # 2. Link regular assemblies to root
    for assembly in regular_assemblies:
        assemblies.append(root_assembly)
        components.append(assembly)
        qty_per.append(random.randint(1, 5))
        scrap.append(round(random.uniform(0, 0.15), 2))

        # Mark assembly as used
        used_components.add(assembly)

    # 3. Find any components not yet used and link them directly to root
    unused_components = [p for p in all_parts if p not in used_components and p != root_assembly]

    for component in unused_components:
        assemblies.append(root_assembly)
        components.append(component)
        qty_per.append(random.randint(1, 10))
        scrap.append(round(random.uniform(0, 0.15), 2))

    # Create dataframe
    bom_df = pd.DataFrame({
        'Assembly': assemblies,
        'Component': components,
        'QuantityPer': qty_per,
        'Scrap': scrap
    })

    return bom_df


def generate_historical_supply_orders(part_source_df,  start_date=None, num_days=365):
    """
    Generate random historical supply orders.

    Parameters:
    -----------
    part_source_df : pandas.DataFrame
        Dataframe containing part source data.
    start_date : datetime, optional
        Start date for historical data, defaults to 1 year ago.
    num_days : int, optional
        Number of days of historical data to generate

    Returns:
    --------
    hist_supply_df : pandas.DataFrame
        Dataframe containing historical supply orders.
    """

    if start_date is None:
        start_date = datetime.now() - timedelta(days=num_days)

    # Generate random data
    orders = []
    sources = []
    order_dates = []
    order_due_dates = []
    quantities = []
    receipt_quantities = []
    statistical_dates = []

    # For each part-source combination
    for _, row in part_source_df.iterrows():
        part = row['Part_Name']
        source = row['Source']
        lead_time = row['EffLeadTime']

        # Generate 5-15 orders per year for each part-source
        num_orders = random.randint(5, 15)

        for _ in range(num_orders):
            # Random order date within the time period
            days_offset = random.randint(0, num_days)
            order_date = start_date + timedelta(days=days_offset)

            # Due date is order date + lead time
            order_due_date = order_date + timedelta(days=lead_time)

            # Statistical date might be slightly different (supplier's commitment)
            stat_date_offset = random.randint(-2, 2)
            statistical_date = order_due_date + timedelta(days=stat_date_offset)

            # Random quantity
            quantity = random.randint(10, 100)

            # Receipt quantity might be slightly different (partial deliveries)
            receipt_quantity = quantity
            if random.random() < 0.1: # 10% chance of partial deliveries
                receipt_quantity = int(quantity * random.uniform(0.8, 0.95))

            orders.append(f"SO{random.randint(10000, 99999)}")
            sources.append(source)
            order_dates.append(order_date.strftime("%Y-%m-%d"))
            order_due_dates.append(order_due_date.strftime("%Y-%m-%d"))
            quantities.append(quantity)
            receipt_quantities.append(receipt_quantity)
            statistical_dates.append(statistical_date.strftime("%Y-%m-%d"))

    # Create dataframe
    hist_supply_df = pd.DataFrame({
        'Order': orders,
        'Source': sources,
        'OrderDate': order_dates,
        'OrderDueDate': order_due_dates,
        'Quantity': quantities,
        'ReceiptQuantity': receipt_quantities,
        'StatisticalDate': statistical_dates
    })

    return hist_supply_df


def generate_historical_demand(part_df, start_date=None, num_days=365):
    """
    Generate random historical demand data.

    Parameters:
    -----------
    part_df : pandas.DataFrame
        Dataframe containing part data.
    start_date : datetime, optional
        Start date for historical data, defaults to 1 year ago.
    num_days : int, optional
        Number of days of historical data to generate

    Returns:
    --------
    hist_demand_df : pandas.DataFrame
        Dataframe containing historical demand data.
    """

    if start_date is None:
        start_date = datetime.now() - timedelta(days=num_days)

    # Generate random data
    orders = []
    part_names = []
    order_quantities = []
    customer_request_dates = []
    actual_ship_dates = []
    actual_receipt_dates = []
    begin_dates = []
    end_dates = []

    # For each part
    for part in part_df['Name']:
        # Generate 10-20 orders per year for each part
        num_orders = random.randint(10, 20)

        for _ in range(num_orders):
            # Random begin date within the time period
            days_offset = random.randint(0, num_days - 30) # leaving room for end date
            begin_date = start_date + timedelta(days=days_offset)

            # End date is 1-30 days after begin date
            end_date_offset = random.randint(1, 30)
            end_date = begin_date + timedelta(days=end_date_offset)

            # Customer request date is between begin and end date
            req_date_offset = random.randint(0, end_date_offset)
            customer_request_date = begin_date + timedelta(days=req_date_offset)

            # Actual ship date might be before or after request date
            ship_date_offset = random.randint(-5, 10)
            actual_ship_date = customer_request_date + timedelta(days=ship_date_offset)

            # Actual receipt date is ship date + shipping time
            shipping_time = random.randint(1, 5)
            actual_receipt_date = actual_ship_date + timedelta(days=shipping_time)

            # Random quantity
            quantity = random.randint(5, 50)

            orders.append(f"DO{random.randint(10000, 99999)}")
            part_names.append(part)
            order_quantities.append(quantity)
            customer_request_dates.append(customer_request_date.strftime("%Y-%m-%d"))
            actual_ship_dates.append(actual_ship_date.strftime("%Y-%m-%d"))
            actual_receipt_dates.append(actual_receipt_date.strftime("%Y-%m-%d"))
            begin_dates.append(begin_date.strftime("%Y-%m-%d"))
            end_dates.append(end_date.strftime("%Y-%m-%d"))

    # Create dataframe
    hist_demand_df = pd.DataFrame({
        'Order': orders,
        'Part_Name': part_names,
        'OrderQuantity': order_quantities,
        'CustomerRequestDate': customer_request_dates,
        'ActualShipDate': actual_ship_dates,
        'ActualReceiptDate': actual_receipt_dates,
        'BeginDate': begin_dates,
        'EndDate': end_dates
        })

    return hist_demand_df


def generate_all_random_data(output_dir='data/random_data', num_parts=20):
    """
    Generate all random data and save to excel.

    Parameters:
    -----------
    output_dir : str, optional
        Directory to save the excel files
    num_parts : int
        Number of parts to generate
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate part data
    part_df = generate_part_data(num_parts)
    part_df.to_excel(os.path.join(output_dir, 'part_data.xlsx'), index=False)

    # Generate supply type data
    supply_type_df = generate_supply_type_data(part_df)
    supply_type_df.to_excel(os.path.join(output_dir, 'supply_type_data.xlsx'), index=False)

    # Generate part source data
    part_source_df = generate_part_source_data(supply_type_df)
    part_source_df.to_excel(os.path.join(output_dir, 'part_source_data.xlsx'), index=False)

    # Generate BOM data
    bom_df = generate_bom_data(supply_type_df)
    bom_df.to_excel(os.path.join(output_dir, 'bom_data.xlsx'), index=False)

    # Generate historical supply orders
    hist_supply_df = generate_historical_supply_orders(part_source_df)
    hist_supply_df.to_excel(os.path.join(output_dir, 'historical_supply_orders.xlsx'), index=False)

    # Generate historical demand
    hist_demand_df = generate_historical_demand(part_df)
    hist_demand_df.to_excel(os.path.join(output_dir, 'historical_demand.xlsx'), index=False)

    print(f"Generated random data saved to {output_dir}/")

    return None
    # return {
    #     'part_df': part_df,
    #     'supply_type_df': supply_type_df,
    #     'part_source_df': part_source_df,
    #     'bom_df': bom_df,
    #     'hist_supply_df': hist_supply_df,
    #     'hist_demand_df': hist_demand_df
    # }