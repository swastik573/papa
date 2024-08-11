import React, { useEffect, useState } from 'react';
import DifferencesTable from './DifferencesTable';

const FileUpload = () => {
  const [filePortal, setFilePortal] = useState(null);
  const [fileBooks, setFileBooks] = useState(null);
  const [data, setData] = useState([]);
  const [detailData, setDetailData] = useState([]);
  const [selectedGST, setSelectedGST] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('portal_file', filePortal);
    formData.append('books_file', fileBooks);

    try {
      const response = await fetch('http://127.0.0.1:5000/uploads', {
        method: 'POST',
        body: formData,
      });

     
        const Data = await response.json();
        setData(Data);
        console.log('Data:', data);
     
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  };

  const fetchDetails = async (gstNumber) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/details', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ gst_number: gstNumber, matching_invoices: data }),
      });

      if (response.ok) {
        const detailData = await response.json();
        setDetailData(detailData);
        console.log('Detail Data:', detailData);
      } else {
        console.error('Fetching details failed');
      }
    } catch (error) {
      console.error('Error fetching details:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRowClick = (gstNumber) => {
    setSelectedGST(gstNumber);
    fetchDetails(gstNumber);
  };
   console.log('data:', data);
  return (
    <div>
      {data.length !== 0 ? (
        <>
          <DifferencesTable
            differences={data}
            onRowClick={handleRowClick}
            detailData={detailData}
            selectedGST={selectedGST}
            isLoading={isLoading}
          />
        </>
      ) : (
        <>
          <input type="file" onChange={(e) => setFilePortal(e.target.files[0])} />
          <input type="file" onChange={(e) => setFileBooks(e.target.files[0])} />
          <button onClick={handleUpload}>Upload Files</button>
        </>
      )}
    </div>
  );
};

export default FileUpload;

