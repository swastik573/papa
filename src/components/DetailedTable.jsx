import React, { useState } from 'react';

const DetailedTable = ({ gstNumber, showDetails }) => {
  const [detailedData, setDetailedData] = useState([]);

  const handleShowDetails = async () => {
    try {
      const response = await fetch('/details', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gst_number: gstNumber }),
      });

      if (response.ok) {
        const data = await response.json();
        setDetailedData(data.html_table); // Handle detailed table data
      } else {
        console.error('Error fetching detailed data');
      }
    } catch (error) {
      console.error('Error fetching detailed data:', error);
    }
  };

  return (
    <div>
      <button onClick={handleShowDetails}>Show Details</button>
      <div dangerouslySetInnerHTML={{ __html: detailedData }} />
    </div>
  );
};

export default DetailedTable;
