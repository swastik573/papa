import React, { useState } from 'react';
import './style1.css'
const DifferencesTable = ({ differences, onRowClick, detailData, selectedGST, isLoading }) => {
  const [expandedGST, setExpandedGST] = useState(null);
  console.log('diff' , differences);
  const handleRowClick = (gstNumber) => {
    if (expandedGST === gstNumber) {
      setExpandedGST(null); // Collapse if the same row is clicked
    } else {
      setExpandedGST(gstNumber); // Expand the new row
      onRowClick(gstNumber); // Fetch details
    }
  };

  return (
    <table className="table">
      <thead>
        <tr>
          <th>GST Number</th>
          <th>Company Name</th>
          <th>Tax Amount Portal</th>
          <th>Tax Amount Books</th>
          <th>Difference Tax</th>
        </tr>
      </thead>
      <tbody>
        {differences.map((item, index) => (
          <React.Fragment key={index}>
            <tr onClick={() => handleRowClick(item['GST Number'])}>
              <td>{item['GST Number']}</td>
              <td>{item['Company Name']}</td>
              <td>{item['Tax Amount_Portal']}</td>
              <td>{item['Tax Amount_Books']}</td>
              <td>{item['Difference_Tax']}</td>
            </tr>
            {expandedGST === item['GST Number'] && (
              <tr>
                <td colSpan="5">
                  {isLoading ? (
                    <p>Loading...</p>
                  ) : (
                    selectedGST === item['GST Number'] && detailData.length > 0 && (
                      <DetailsTable details={detailData} />
                    )
                  )}
                </td>
              </tr>
            )}
          </React.Fragment>
        ))}
      </tbody>
    </table>
  );
};

const DetailsTable = ({ details }) => {
  return (
    <table className="table details-table">
      <thead>
        <tr>
          <th>Portal Invoice Number</th>
          <th>Portal Tax Amount</th>
          <th>Books Invoice Number</th>
          <th>Books Tax Amount</th>
          <th>Tax Amount Difference</th>
        </tr>
      </thead>
      <tbody>
        {details.map((item, index) => (
          <tr key={index}>
            <td>{item['Portal Invoice Number']}</td>
            <td>{item['Portal Tax Amount']}</td>
            <td>{item['Books Invoice Number']}</td>
            <td>{item['Books Tax Amount']}</td>
            <td>{item['Tax Amount Difference']}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default DifferencesTable;
