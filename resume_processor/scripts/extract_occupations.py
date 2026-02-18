import pandas as pd

def get_matching_occupations(file1_path, file2_path):
    """
    Compare ACS IT occupations with ANZSCO occupations and
    return matching occupations as a list of dictionaries.

    Each dictionary contains:
        - code
        - category
        - name
    """

    # Load ACS IT occupations
    acs_df = pd.read_csv(file1_path, dtype=str)

    # Extract relevant codes
    major_groups = set(acs_df["Major Group"].dropna().astype(str))
    unit_groups = set(acs_df["Subgroup/Unit Group"].dropna().astype(str))

    # Load ANZSCO occupations
    anzsco_df = pd.read_csv(file2_path, dtype=str)

    # Keep only rows that have a valid occupation code
    anzsco_df = anzsco_df[anzsco_df["Occupation Code"].str.isdigit().fillna(False)]

    # Ensure codes are strings
    anzsco_df["Occupation Code"] = anzsco_df["Occupation Code"].astype(str)

    matching_occupations = []

    for _, row in anzsco_df.iterrows():
        occ_code = row["Occupation Code"]
        occ_name = row["Description"]
        occ_category = row["Category"]

        # Extract 4-digit unit group from 6-digit ANZSCO code
        unit_group_code = occ_code[:4]

        # Match if:
        # - Exact 6-digit match with ACS unit group
        # - OR 4-digit unit group matches ACS major group
        if occ_code in unit_groups or unit_group_code in major_groups:
            matching_occupations.append({
                "code": occ_code,
                "category": occ_category,
                "name": occ_name
            })

    return matching_occupations

def main():
    matches = get_matching_occupations(
        "data/acs_it_occupations.csv",
        "data/anzsco_occupations.csv"
    )

    for m in matches[:10]:
        print(m)

    print(f"Total occupations: {len(matches)}")

if __name__ == "__main__":
    main()
