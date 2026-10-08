const OCSAPreview = ({ certificate }) => {

    const formatDate = (date) => {
        return new Date(date).toLocaleDateString("en-GB", {
            day: "numeric",
            month: "short",
            year: "numeric",
        });
    };

    return (
        <div className="relative w-full">
            {/* Certificate Background */}
            <img
                src="/OCSA-preview.png"
                alt="OCSA Certificate"
                className="block h-auto w-full"
            />

            {/* Issued Date */}
            <div
                className="ocsp-issued-date absolute font-medium text-black">
                {formatDate(certificate.issuedDate)}
            </div>

            {/* Certificate ID */}
            <div
                className="ocsp-certificate-id absolute font-medium text-black">
                {certificate.certificateId}
            </div>

            {/* Student Name */}
            <div
                className="student-name absolute left-1/2 -translate-x-1/2 text-center font-semibold text-black">
                {certificate.studentName}
            </div>
        </div>
    );
};

export default OCSAPreview;