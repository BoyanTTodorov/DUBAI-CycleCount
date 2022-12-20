from fileinput import filename
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QMainWindow,QApplication,QMessageBox,QFileDialog
import traceback
import sys
from os import path
from PyQt6.uic import loadUiType
FORM_CLASS,_ = loadUiType(path.join(path.dirname('__file__'), 'main.ui'))

import sqlite3
import pandas as pd
from datetime import datetime


class Main(QMainWindow, FORM_CLASS):
    def __init__(self, parent= None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setGeometry(0,0, 705,725)
        self.Handel_Buttons()
        self.Search_Button()
        self.Update_Labels()
        self.Generate_Excel_File()
        # self.Browse_Files()
        # self.Update_Button()
        self.Update_Button()
        self.setFixedSize(self.size())
        
    def showdialog(self, str):
        QMessageBox.about(self, "Bin's report", str)

    # def AUTO_UPDATE(self):
    #     self.showdialog('UPDATING PLEASE WAIT...')
    #     df = pd.read_excel(r'S:\Warehouse dept\Inventory control\Reporting and dashboards\Cycle Counting Posting DUBAI\Cycle_Counting_DUBAI.xlsm')
    #     df['Counted'] = df.sum(axis=1).astype(int)
    #     df_update = df[['Bin', 'Counted']]
    #     df_update = df_update.iloc[1:,:]
    #     df_update = df_update.set_index('Bin')
    #     db = sqlite3.connect('DATABASE\countings_dubai.db')
    #     df_update.to_sql('countings', db, if_exists='replace')
    #     db.commit()
    #     db.close()
    #     #counting_gif.LoadingGif.stopAnimation(self)
    #     self.showdialog('UPDATE DONE...')

    def GetFiles(self):
        filename = QFileDialog.getOpenFileName(self,'Single File','C:\'','*.xlsx')
        df = pd.read_excel(filename[0])
        db_path = r"DATABASE\countings_dubai.db"
        df = df['Storage Bin']
        conn = sqlite3.connect(db_path)
        curs = conn.cursor()

        try:
            for bin in df:
                curs.execute(f'UPDATE countings SET Counted = 1 WHERE "{bin}" = Bin')
                print(f'Updating DUBAI Database with Bin {bin}')
                total = list(curs.execute(f'SELECT COUNT(*) FROM countings WHERE Counted > 0;'))
                print(str(total[0]) + ' Counted')
            conn.commit()
            curs.close()
            conn.close()

        except sqlite3.Error as err:
                    print('SQLite error: %s' % (' '.join(err.args)))
                    print("Exception class is: ", err.__class__)
                    print('SQLite traceback: ')
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    print(traceback.format_exception(exc_type, exc_value, exc_tb))
        self.showdialog('FILE UPLOADED...')


    def GET_BIN_DATA(self):
        # self.AUTO_UPDATE()
        current_day = datetime.date(datetime.now())
        user_input = int(self.bin_qty_2.text())
        db = sqlite3.connect('DATABASE\countings_dubai.db')
        command = f'''SELECT * FROM countings ORDER BY counted ASC LIMIT "{user_input}"'''
        df = pd.read_sql(command, db)
        df = df.set_index('Bin')
        df.to_excel('Generated Report\Bins '+ str(current_day) +'.xlsx')
        db.close()
        self.showdialog('FILE GENERATED...')

    def Update_Labels(self):
        ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
        current_day = datetime.date(datetime.now())
        days_left = int((ending_day_of_current_year - current_day).days)
        db = sqlite3.connect('DATABASE\countings_dubai.db')
        cursor2=db.cursor()
        total_bins= '''SELECT COUNT(*) FROM countings'''
        cursor2.execute(total_bins)
        total = [int(row[0]) for row in cursor2.fetchall()][0]
        self.lbl_total_bins.setText(str(total))
        cursor3=db.cursor()
        counted_bins= '''SELECT COUNT(*) FROM countings WHERE Counted > 0'''
        cursor3.execute(counted_bins)
        counted = [int(row[0]) for row in cursor3.fetchall()][0]
        self.lbl_scanned.setText(str(counted))
        per_day = int((total - counted) / days_left)
        self.lbl_daily.setText(str(per_day))
        db.close()

    # def Browse_Files(self):
    #     self.btn_upload.clicked.connect(self.getfiles)

    def Generate_Excel_File(self):
        self.btn_generate_2.clicked.connect(self.GET_BIN_DATA)

    def Search_Button(self):
        self.search_btn.clicked.connect(self.GET_SEARCH)
    
    def Handel_Buttons(self):
        self.refresh_btn.clicked.connect(self.GET_DATA)
     
    def GET_SEARCH(self):
        user_input = str(self.search_box.text())
        db = sqlite3.connect('DATABASE\countings_dubai.db')
        cursor = db.cursor()
        command = f'''SELECT * FROM countings WHERE bin = "{user_input}"'''
        result = cursor.execute(command)
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))        
        db.close()

    def GET_DATA(self):
        db = sqlite3.connect('DATABASE\countings_dubai.db')
        cursor = db.cursor()
        command = '''SELECT * FROM countings'''
        result = cursor.execute(command)
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))  
        db.close()

    def Update_Button(self):
        self.btn_update.clicked.connect(self.GetFiles)


def main():
    app = QApplication(sys.argv)
    window = Main()
    # window.AUTO_UPDATE()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()