import pandas as pd

# Load the CSV file
df = pd.read_csv('/home/evilscript/Downloads/npc.csv')

# Define the classification columns
class_cols = ['Luigi', 'Fede', 'Amon']

# Fill NaN values with an empty string to standardize the dataframe
df[class_cols] = df[class_cols].fillna('')

# Define the function to determine agreement
def classify_agreement(row):
    if len(set(row[class_cols])) == 1:
        return 'Total Agreement'
    return 'No Total Agreement'

def classify_agreement_type(row):
    if row['Agreement'] == 'Total Agreement':
        if row[class_cols[0]] == 'x':
            return 'OUT'
        elif row[class_cols[0]] == '':
            return 'OK'
    return 'N/A'  # Not applicable

# Apply the function to each row
df['Agreement'] = df.apply(classify_agreement, axis=1)
df['Agreement Type'] = df.apply(classify_agreement_type, axis=1)

# Count the number of each type of agreement
total_agreement_count = (df['Agreement'] == 'Total Agreement').sum()
no_total_agreement_count = (df['Agreement'] == 'No Total Agreement').sum()

# Calculate other statistics
any_doubts_count = (df[class_cols] == '?').any(axis=1).sum()

# Count 'in', 'out', and 'doubtful' for each reviewer
in_counts = (df[class_cols] == '').sum()
out_counts = (df[class_cols] == 'x').sum()
doubtful_counts = (df[class_cols] == '?').sum()

# Create a DataFrame for statistics
stats = pd.DataFrame({
    'Total Agreement': [total_agreement_count],
    'No Total Agreement': [no_total_agreement_count],
    'Any Doubts': [any_doubts_count],
    'In Count Luigi': [in_counts['Luigi']],
    'In Count Fede': [in_counts['Fede']],
    'In Count Amon': [in_counts['Amon']],
    'Out Count Luigi': [out_counts['Luigi']],
    'Out Count Fede': [out_counts['Fede']],
    'Out Count Amon': [out_counts['Amon']],
    'Doubtful Count Luigi': [doubtful_counts['Luigi']],
    'Doubtful Count Fede': [doubtful_counts['Fede']],
    'Doubtful Count Amon': [doubtful_counts['Amon']],
})

# Save the papers with total agreement further separated into 'OK papers' and 'OUT papers'
ok_papers = df[(df['Agreement'] == 'Total Agreement') & (df['Agreement Type'] == 'OK')]
out_papers = df[(df['Agreement'] == 'Total Agreement') & (df['Agreement Type'] == 'OUT')]

# Write to an Excel file
with pd.ExcelWriter('papers_statistics.xlsx') as writer:
    stats.to_excel(writer, sheet_name='Statistics', index=False)
    ok_papers.to_excel(writer, sheet_name='OK Papers', index=False)
    out_papers.to_excel(writer, sheet_name='OUT Papers', index=False)
    df[df['Agreement'] == 'No Total Agreement'].to_excel(writer, sheet_name='No Total Agreement', index=False)

print('Excel file created with the statistics and separate sheets for OK papers and OUT papers.')