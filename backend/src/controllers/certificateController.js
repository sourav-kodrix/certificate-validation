const Certificate = require("../models/Certificate");

const createCertificate = async (req, res, next) => {
    try {
        const certificate = await Certificate.create(req.body);

        res.status(201).json({
            success: true,
            message: "Certificate created successfully",
            certificate,
        });
    } catch (error) {
        next(error);
    }
};

const getCertificate = async (req, res, next) => {
    try {
        const { certificateId } = req.params;

        const normalizedCertificateId = certificateId.replace(/\s+/g, "");

        const certificate = await Certificate.findOne({
            $expr: {
                $eq: [
                    {
                        $toLower: {
                            $replaceAll: {
                                input: "$certificateId",
                                find: " ",
                                replacement: "",
                            },
                        },
                    },
                    normalizedCertificateId.toLowerCase(),
                ],
            },
        }).lean();

        if (!certificate) {
            return res.status(404).json({
                success: false,
                message: "Certificate not found",
            });
        }

        res.status(200).set("Cache-Control", "no-store").json({
            success: true,
            certificate,
        });
    } catch (error) {
        next(error);
    }
};

module.exports = {
    createCertificate,
    getCertificate,
};