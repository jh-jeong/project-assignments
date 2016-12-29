/** 
 * CS360 hw4
 * File name: example.java   
 * Last modified: 2015/4/6   
 * Comment: Sample java source code for connection Oracle Database             
 * Try to refer to this guideline when you perform HW4 
 * */



import java.sql.*;

class Example{
    public static void main(String[] args)  {
        Connection con = null;
        Statement stmt = null;

        try {
            Class.forName("oracle.jdbc.driver.OracleDriver");

	     /** In order to create valid connection
             You need to change the second, third parameter of getConnection method 
         **/ 	     

        con = DriverManager.getConnection( "jdbc:oracle:thin:@dbclick.kaist.ac.kr:1521:orcl", "s20120864", "123qweasd");
	    System.out.println("Connection created!");

	    
		/**
		 *  Sending query statement to database ( Try it!) 
		 **/
	    
	    /*
	    stmt = con.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM users");

            while (rs.next()) {
                String product = rs.getString(1);
                System.out.println(product);
            }

	    */

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                if (stmt != null) stmt.close();
                if (con != null) con.close();
            } catch (Exception e) { }
        }
    }
}
