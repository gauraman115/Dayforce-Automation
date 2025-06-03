# from flask import Flask, render_template, request
# import pandas as pd
# from collections import defaultdict
# import os
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# def excel_col_letter_to_index(letter):
#     """Convert Excel column letter to 0-based index"""
#     letter = letter.upper()
#     index = 0
#     for char in letter:
#         index = index * 26 + (ord(char) - ord('A') + 1)
#     return index - 1

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/generate', methods=['POST'])
# def generate():
#     input_count = int(request.form['inputCount'])
#     input_fields_pos = {}

#     for i in range(input_count):
#         name = request.form[f'input_name_{i}']
#         row_col = request.form[f'input_pos_{i}'].split(',')
#         row, col = int(row_col[0]), row_col[1].strip()
#         input_fields_pos[name] = (col, row)

#     output_name = request.form['output_name']
#     out_row_col = request.form['output_pos'].split(',')
#     output_field_pos = (out_row_col[1].strip(), int(out_row_col[0]))

#     excel_file = request.files['excel_file']
#     filename = secure_filename(excel_file.filename)
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     excel_file.save(filepath)

#     # Load raw Excel
#     df_raw = pd.read_excel(filepath, header=None)

#     # Get input/output headers
#     input_fields_idx = {
#         key: (row - 1, excel_col_letter_to_index(col))
#         for key, (col, row) in input_fields_pos.items()
#     }
#     output_row_idx, output_col_idx = output_field_pos[1] - 1, excel_col_letter_to_index(output_field_pos[0])

#     mapped_columns = {
#         field: df_raw.iat[row_idx, col_idx]
#         for field, (row_idx, col_idx) in input_fields_idx.items()
#     }
#     output_column_name = df_raw.iat[output_row_idx, output_col_idx]
#     data_start_row = max([r for r, _ in input_fields_idx.values()] + [output_row_idx]) + 1

#     # Read data rows
#     df = pd.read_excel(filepath, skiprows=data_start_row, header=None)

#     max_col_idx = max([c for _, c in input_fields_idx.values()] + [output_col_idx])
#     column_names = []
#     for col_idx in range(max_col_idx + 1):
#         name = None
#         for field, (_, f_col) in input_fields_idx.items():
#             if f_col == col_idx:
#                 name = field
#         if col_idx == output_col_idx:
#             name = output_column_name
#         column_names.append(name if name else f"Unused_{col_idx}")
#     df.columns = column_names

#     # Grouping
#     grouped_conditions = defaultdict(list)
#     for _, row in df.iterrows():
#         output_val = row[output_column_name]
#         condition_parts = []
#         for field in input_fields_pos.keys():
#             val = row[field]
#             condition_parts.append(f"{field} = '{val}'")
#         condition = " and ".join(condition_parts)
#         grouped_conditions[output_val].append(f"({condition})")

#     # Generate XSLT
#     xslt_lines = ['<xsl:choose>']
#     for output_val, conditions in grouped_conditions.items():
#         condition_block = " or\n  ".join(conditions)
#         xslt_lines.append(f'  <xsl:when test="{condition_block}">')
#         xslt_lines.append(f'    <xsl:text>{output_val}</xsl:text>')
#         xslt_lines.append('  </xsl:when>')

#     xslt_lines.append('  <xsl:otherwise>')
#     xslt_lines.append(f'    <xsl:value-of select="' + " / ".join(input_fields_pos.keys()) + '" />')
#     xslt_lines.append('  </xsl:otherwise>')
#     xslt_lines.append('</xsl:choose>')

#     xslt_output = "\n".join(xslt_lines)

#     return f"<pre>{xslt_output}</pre>"

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import pandas as pd
from collections import defaultdict
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def excel_col_letter_to_index(letter):
    """Convert Excel column letter to 0-based index"""
    letter = letter.upper()
    index = 0
    for char in letter:
        index = index * 26 + (ord(char) - ord('A') + 1)
    return index - 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get form data
        input_count = int(request.form['inputCount'])
        input_fields_pos = {}

        for i in range(input_count):
            name = request.form[f'input_name_{i}']
            row_col = request.form[f'input_pos_{i}'].split(',')
            row, col = int(row_col[0]), row_col[1].strip()
            input_fields_pos[name] = (col, row)

        output_name = request.form['output_name']
        out_row_col = request.form['output_pos'].split(',')
        output_field_pos = (out_row_col[1].strip(), int(out_row_col[0]))

        excel_file = request.files['excel_file']
        if excel_file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400

        filename = secure_filename(excel_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        excel_file.save(filepath)

        # Load raw Excel
        df_raw = pd.read_excel(filepath, header=None)

        # Get input/output headers
        input_fields_idx = {
            key: (row - 1, excel_col_letter_to_index(col))
            for key, (col, row) in input_fields_pos.items()
        }

        output_row_idx, output_col_idx = output_field_pos[1] - 1, excel_col_letter_to_index(output_field_pos[0])

        # Extract the header names
        mapped_columns = {
            field: df_raw.iat[row_idx, col_idx]
            for field, (row_idx, col_idx) in input_fields_idx.items()
        }

        output_column_name = df_raw.iat[output_row_idx, output_col_idx]
        data_start_row = max([r for r, _ in input_fields_idx.values()] + [output_row_idx]) + 1

        # Read data rows
        df = pd.read_excel(filepath, skiprows=data_start_row, header=None)

        # Determine max column index
        max_col_idx = max([c for _, c in input_fields_idx.values()] + [output_col_idx])
        column_names = []

        for col_idx in range(max_col_idx + 1):
            name = None
            for field, (_, f_col) in input_fields_idx.items():
                if f_col == col_idx:
                    name = field
            if col_idx == output_col_idx:
                name = output_column_name
            column_names.append(name if name else f"Unused_{col_idx}")

        df.columns = column_names

        # Grouping conditions
        grouped_conditions = defaultdict(list)

        for _, row in df.iterrows():
            output_val = row[output_column_name]
            condition_parts = [f"{field} = '{row[field]}'" for field in input_fields_pos.keys()]
            condition = " and ".join(condition_parts)
            grouped_conditions[output_val].append(f"({condition})")

        # Generate XSLT
        xslt_lines = ['<xsl:choose>']
        for output_val, conditions in grouped_conditions.items():
            condition_block = " or\n        ".join(conditions)
            xslt_lines.append(f'    <xsl:when test="{condition_block}">')
            xslt_lines.append(f'        <xsl:text>{output_val}</xsl:text>')
            xslt_lines.append('    </xsl:when>')
        
        xslt_lines.append('    <xsl:otherwise>')
        xslt_lines.append(f'        <xsl:value-of select="' + " / ".join(input_fields_pos.keys()) + '" />')
        xslt_lines.append('    </xsl:otherwise>')
        xslt_lines.append('</xsl:choose>')

        xslt_output = "\n".join(xslt_lines)

        return jsonify({
            'success': True,
            'output': xslt_output
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(port=5000)
